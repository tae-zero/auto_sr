import httpx
import logging
import time
from typing import Dict, Optional, Any
from fastapi import HTTPException, Request
from fastapi.responses import Response, StreamingResponse
import json

logger = logging.getLogger(__name__)

class ProxyService:
    """프록시 서비스 클래스"""
    
    def __init__(self, service_discovery, timeout: int = 30):
        self.service_discovery = service_discovery
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def forward_request(self, service_name: str, path: str, method: str, 
                            headers: Dict, body: Optional[bytes] = None, 
                            query_params: Dict = None) -> Dict:
        """요청을 대상 서비스로 전달"""
        
        start_time = time.time()
        instance = None
        
        try:
            # 서비스 인스턴스 선택
            instance = self.service_discovery.get_service_instance(service_name)
            if not instance:
                raise HTTPException(status_code=503, detail=f"Service {service_name} not available")
            
            # 대상 URL 구성
            target_url = f"{instance.url}{path}"
            
            # 쿼리 파라미터 추가
            if query_params:
                query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
                target_url = f"{target_url}?{query_string}"
            
            # 헤더 정리 (불필요한 헤더 제거)
            clean_headers = self._clean_headers(headers)
            
            logger.info(f"Forwarding {method} request to {target_url}")
            
            # 요청 전달
            response = await self.client.request(
                method=method,
                url=target_url,
                headers=clean_headers,
                content=body
            )
            
            response_time = time.time() - start_time
            
            # 응답 로깅
            logger.info(f"Response from {service_name}: {response.status_code} ({response_time:.3f}s)")
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.content,
                "service": service_name,
                "target_url": target_url,
                "response_time": response_time,
                "instance": instance.host + ":" + str(instance.port)
            }
            
        except httpx.TimeoutException:
            logger.error(f"Timeout error for service {service_name}")
            raise HTTPException(status_code=504, detail=f"Service {service_name} timeout")
            
        except httpx.ConnectError:
            logger.error(f"Connection error for service {service_name}")
            raise HTTPException(status_code=503, detail=f"Service {service_name} connection failed")
            
        except HTTPException:
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error forwarding request to {service_name}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
            
        finally:
            # 인스턴스 연결 해제
            if instance:
                self.service_discovery.release_instance(service_name, instance)
    
    def _clean_headers(self, headers: Dict) -> Dict:
        """헤더 정리 (불필요한 헤더 제거)"""
        cleaned = {}
        exclude_headers = {
            'host', 'content-length', 'transfer-encoding', 
            'connection', 'keep-alive', 'proxy-connection'
        }
        
        for key, value in headers.items():
            if key.lower() not in exclude_headers:
                cleaned[key] = value
        
        return cleaned
    
    async def handle_request(self, request: Request, service_name: str, path: str) -> Response:
        """요청 처리 및 응답 반환"""
        
        # 요청 본문 읽기
        body = await request.body()
        
        # 쿼리 파라미터 추출
        query_params = dict(request.query_params)
        
        # 프록시 요청 전달
        result = await self.forward_request(
            service_name=service_name,
            path=f"/{path}",
            method=request.method,
            headers=dict(request.headers),
            body=body,
            query_params=query_params
        )
        
        # 응답 헤더 설정
        response_headers = result["headers"]
        
        # CORS 헤더 추가
        response_headers["Access-Control-Allow-Origin"] = "*"
        response_headers["Access-Control-Allow-Methods"] = "*"
        response_headers["Access-Control-Allow-Headers"] = "*"
        
        # Gateway 정보 헤더 추가
        response_headers["X-Gateway-Service"] = service_name
        response_headers["X-Gateway-Instance"] = result["instance"]
        response_headers["X-Gateway-Response-Time"] = f"{result['response_time']:.3f}s"
        
        # 스트리밍 응답인지 확인
        if "transfer-encoding" in response_headers and response_headers["transfer-encoding"] == "chunked":
            return StreamingResponse(
                iter([result["content"]]),
                status_code=result["status_code"],
                headers=response_headers
            )
        else:
            return Response(
                content=result["content"],
                status_code=result["status_code"],
                headers=response_headers
            )
    
    async def health_check_service(self, service_name: str) -> Dict:
        """서비스 헬스 체크"""
        try:
            result = await self.forward_request(
                service_name=service_name,
                path="/health",
                method="GET",
                headers={"Content-Type": "application/json"},
                body=None
            )
            
            return {
                "service": service_name,
                "status": "healthy" if result["status_code"] == 200 else "unhealthy",
                "response_time": result["response_time"],
                "instance": result["instance"]
            }
            
        except Exception as e:
            return {
                "service": service_name,
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def close(self):
        """리소스 정리"""
        await self.client.aclose() 