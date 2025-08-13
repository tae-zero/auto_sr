"""
Gateway Auth 서비스
- 인증 비즈니스 로직 처리
- 토큰 검증 및 관리
- 프록시 요청 처리 및 서비스 디스커버리
"""
from typing import Dict, Any, Optional
import httpx
import logging
import os
import time
from fastapi import HTTPException, Request
from app.domain.auth.repository.auth_repository import AuthRepository
from app.domain.auth.model.auth_model import AuthRequest, AuthResponse
from app.domain.auth.entity.auth_entity import AuthEntity

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.repository = AuthRepository()
        self.auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://localhost:8008")
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def process_signup(self, request: AuthRequest) -> Dict[str, Any]:
        """회원가입 처리"""
        try:
            # 비즈니스 로직 검증
            self._validate_signup_request(request)
            
            # Auth Service로 요청 전달
            response = await self._forward_to_auth_service("/signup", request.dict())
            
            # 결과 저장
            auth_entity = AuthEntity(
                user_id=response.get("user_id"),
                email=request.email,
                company_id=request.company_id,
                status="active"
            )
            await self.repository.save_auth_data(auth_entity)
            
            return response
            
        except Exception as e:
            logger.error(f"회원가입 처리 실패: {str(e)}")
            raise Exception(f"회원가입 처리 실패: {str(e)}")
    
    async def process_login(self, request: AuthRequest) -> Dict[str, Any]:
        """로그인 처리"""
        try:
            # 비즈니스 로직 검증
            self._validate_login_request(request)
            
            # Auth Service로 요청 전달
            response = await self._forward_to_auth_service("/login", request.dict())
            
            # 로그인 기록 저장
            await self.repository.log_login_attempt(
                email=request.email,
                success=True,
                timestamp=response.get("timestamp")
            )
            
            return response
            
        except Exception as e:
            logger.error(f"로그인 처리 실패: {str(e)}")
            raise Exception(f"로그인 처리 실패: {str(e)}")
    
    async def validate_token(self, auth_header: str) -> Dict[str, Any]:
        """토큰 검증"""
        try:
            # Auth Service로 토큰 검증 요청
            response = await self._forward_to_auth_service(
                "/validate", 
                {"token": auth_header.replace("Bearer ", "")},
                headers={"Authorization": auth_header}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"토큰 검증 실패: {str(e)}")
            raise Exception(f"토큰 검증 실패: {str(e)}")
    
    async def refresh_token(self, auth_header: str) -> Dict[str, Any]:
        """토큰 갱신"""
        try:
            # Auth Service로 토큰 갱신 요청
            response = await self._forward_to_auth_service(
                "/refresh", 
                {"token": auth_header.replace("Bearer ", "")},
                headers={"Authorization": auth_header}
            )
            
            return response
            
        except Exception as e:
            logger.error(f"토큰 갱신 실패: {str(e)}")
            raise Exception(f"토큰 갱신 실패: {str(e)}")
    
    # 🔧 프록시 기능 통합
    async def forward_request(self, service_name: str, path: str, method: str, 
                            headers: Dict, body: Optional[bytes] = None, 
                            query_params: Dict = None, files: Dict = None) -> Dict:
        """요청을 대상 서비스로 전달 (프록시 기능)"""
        
        start_time = time.time()
        
        try:
            # 서비스 디스커버리에서 인스턴스 선택
            from app.domain.discovery.service_discovery import ServiceDiscovery
            service_discovery = ServiceDiscovery()
            instance = service_discovery.get_service_instance(service_name)
            
            if not instance:
                raise HTTPException(status_code=503, detail=f"Service {service_name} not available")
            
            # 대상 URL 구성
            target_url = f"http://{instance.host}:{instance.port}{path}"
            
            # 쿼리 파라미터 추가
            if query_params:
                query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
                target_url = f"{target_url}?{query_string}"
            
            # 헤더 정리 (불필요한 헤더 제거)
            clean_headers = self._clean_headers(headers)
            
            logger.info(f"Forwarding {method} request to {target_url}")
            
            # 요청 전달
            response = await self.http_client.request(
                method=method,
                url=target_url,
                headers=clean_headers,
                content=body,
                files=files
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
                "instance": f"{instance.host}:{instance.port}"
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
    
    def _validate_signup_request(self, request: AuthRequest) -> None:
        """회원가입 요청 검증"""
        if not request.email or not request.email.strip():
            raise ValueError("이메일은 필수입니다")
        
        if not request.auth_id or not request.auth_id.strip():
            raise ValueError("아이디는 필수입니다")
        
        if not request.auth_pw or len(request.auth_pw) < 6:
            raise ValueError("비밀번호는 6자 이상이어야 합니다")
        
        if not request.company_id or not request.company_id.strip():
            raise ValueError("회사 ID는 필수입니다")
    
    def _validate_login_request(self, request: AuthRequest) -> None:
        """로그인 요청 검증"""
        if not request.auth_id or not request.auth_id.strip():
            raise ValueError("아이디는 필수입니다")
        
        if not request.auth_pw or not request.auth_pw.strip():
            raise ValueError("비밀번호는 필수입니다")
    
    async def _forward_to_auth_service(
        self, 
        endpoint: str, 
        data: Dict[str, Any], 
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Auth Service로 요청 전달"""
        try:
            default_headers = {
                "Content-Type": "application/json",
                "User-Agent": "Gateway/1.0"
            }
            
            if headers:
                default_headers.update(headers)
            
            response = await self.http_client.post(
                f"{self.auth_service_url}{endpoint}",
                json=data,
                headers=default_headers
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Auth Service 응답 오류: {e.response.status_code}")
            raise Exception(f"Auth Service 응답 오류: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Auth Service 요청 전달 실패: {str(e)}")
            raise Exception(f"Auth Service 요청 전달 실패: {str(e)}")
    
    async def close(self):
        """HTTP 클라이언트 종료"""
        await self.http_client.aclose()
