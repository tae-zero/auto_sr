from fastapi import APIRouter, Request, HTTPException, Header
from typing import Dict, Any
import logging
import httpx
import os

from app.router.auth_router import verify_token
from app.domain.discovery.service_discovery import ServiceDiscovery

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tcfdreport", tags=["tcfdreport"])

# TCFD Report Service URL 가져오기
def get_service_url():
    """환경에 따른 서비스 URL 반환"""
    if os.getenv("RAILWAY_ENVIRONMENT") == "true":
        return os.getenv("RAILWAY_TCFD_REPORT_SERVICE_URL", "")
    return "http://tcfdreport-service:8004"

TCFD_REPORT_SERVICE_URL = get_service_url()

# Docker 환경에서 직접 연결 시도
def get_docker_service_url():
    """Docker 환경에서 직접 서비스 연결"""
    return "http://tcfdreport-service:8004"

def build_service_url(host: str, port: str, environment: str) -> str:
    """환경에 따른 서비스 URL 생성"""
    if environment == "true":  # Railway 환경
        if host.startswith(('http://', 'https://')):
            return host
        else:
            return f"https://{host}"
    else:  # Docker 환경
        if host.startswith(('http://', 'https://')):
            return f"{host}:{port}" if port else host
        else:
            return f"http://{host}:{port}" if port else f"http://{host}"

@router.get("/health")
async def health_check(request: Request):
    """TCFD Report Service 헬스 체크"""
    try:
        logger.info("TCFD Report Service 헬스 체크 요청 시작")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # Docker 환경에서는 직접 연결, Railway 환경에서는 Service Discovery 사용
        if os.getenv("RAILWAY_ENVIRONMENT") == "production":
            # Railway 환경: Service Discovery에서 가져온 host 사용
            final_url = host
        else:
            # Docker 환경: 직접 연결 시도
            final_url = get_docker_service_url()
        
        logger.info(f"TCFD Report Service URL: {final_url}")
        logger.info(f"요청 엔드포인트: {final_url}/health")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{final_url}/health")
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"TCFD Report Service 헬스 체크 성공: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.get("/company-financial-data")
async def get_company_financial_data(request: Request, company_name: str):
    """회사별 재무정보 조회 (TCFD Report Service)"""
    try:
        logger.info(f"TCFD Report Service - 회사별 재무정보 조회 요청 시작: {company_name}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # Docker 환경에서는 직접 연결, Railway 환경에서는 Service Discovery 사용
        if os.getenv("RAILWAY_ENVIRONMENT") == "production":
            # Railway 환경: Service Discovery에서 가져온 host 사용
            final_url = host
        else:
            # Docker 환경: 직접 연결 시도
            final_url = get_docker_service_url()
        
        logger.info(f"TCFD Report Service URL: {final_url}")
        logger.info(f"요청 엔드포인트: {final_url}/api/v1/tcfdreport/company-financial-data")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{final_url}/api/v1/tcfdreport/company-financial-data",
                params={"company_name": company_name}
            )
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"TCFD Report Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.get("/standards")
async def get_tcfd_standards(request: Request):
    """TCFD 표준 정보 조회 (TCFD Report Service)"""
    try:
        logger.info("TCFD Report Service - TCFD 표준 정보 조회 요청 시작")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # Docker 환경에서는 직접 연결, Railway 환경에서는 Service Discovery 사용
        if os.getenv("RAILWAY_ENVIRONMENT") == "production":
            # Railway 환경: Service Discovery에서 가져온 host 사용
            final_url = host
        else:
            # Docker 환경: 직접 연결 시도
            final_url = get_docker_service_url()
        
        logger.info(f"TCFD Report Service URL: {final_url}")
        logger.info(f"요청 엔드포인트: {final_url}/api/v1/tcfdreport/standards")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{final_url}/api/v1/tcfdreport/standards")
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"TCFD Report Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.post("/inputs")
async def create_tcfd_input(request: Request, data: dict):
    """TCFD 입력 데이터 생성"""
    try:
        logger.info("TCFD Report Service - TCFD 입력 데이터 생성 요청 시작")
        
        # 환경변수 상태 확인
        railway_env = os.getenv("RAILWAY_ENVIRONMENT", "false")
        logger.info(f"RAILWAY_ENVIRONMENT: {railway_env}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # Service Discovery 정보 로깅
        logger.info(f"Service Discovery 결과: host={tcfdreport_service.host}, port={tcfdreport_service.port}")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # Docker 환경에서는 직접 연결, Railway 환경에서는 Service Discovery 사용
        if railway_env == "production":
            # Railway 환경: Service Discovery에서 가져온 host 사용
            final_url = host
            logger.info(f"Railway 환경 감지: {final_url} 사용")
        else:
            # Docker 환경: 직접 연결 시도
            final_url = get_docker_service_url()
            logger.info(f"Docker 환경 감지: {final_url} 사용")
        
        url = f"{final_url}/api/v1/tcfdreport/inputs"
        logger.info(f"최종 요청 URL: {url}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 요청 헤더에서 인증 토큰 가져오기
            auth_header = request.headers.get("Authorization")
            headers = {}
            
            if auth_header:
                headers["Authorization"] = auth_header
                logger.info(f"인증 토큰 발견: {auth_header[:20]}...")
            else:
                logger.warning("인증 토큰이 없습니다")
            
            logger.info(f"요청 데이터: {data}")
            logger.info(f"요청 헤더: {headers}")
            
            response = await client.post(
                url,
                json=data,
                headers=headers
            )
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"TCFD Report Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.get("/inputs")
async def get_tcfd_inputs(request: Request):
    """TCFD 입력 데이터 조회"""
    try:
        logger.info("TCFD Report Service - TCFD 입력 데이터 조회 요청 시작")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # Docker 환경에서는 직접 연결, Railway 환경에서는 Service Discovery 사용
        if os.getenv("RAILWAY_ENVIRONMENT") == "production":
            # Railway 환경: Service Discovery에서 가져온 host 사용
            final_url = host
        else:
            # Docker 환경: 직접 연결 시도
            final_url = get_docker_service_url()
        
        logger.info(f"TCFD Report Service URL: {final_url}")
        logger.info(f"요청 엔드포인트: {final_url}/api/v1/tcfdreport/inputs")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{final_url}/api/v1/tcfdreport/inputs")
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"TCFD Report Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.post("/download/word")
async def download_tcfd_report_as_word(request: Request, data: dict):
    """TCFD 보고서를 Word 문서로 다운로드"""
    try:
        logger.info(f"TCFD Report Service - Word 문서 다운로드 요청 시작: {data.get('company_name', 'Unknown')}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # Docker 환경에서는 직접 연결, Railway 환경에서는 Service Discovery 사용
        if os.getenv("RAILWAY_ENVIRONMENT") == "production":
            # Railway 환경: Service Discovery에서 가져온 host 사용
            final_url = host
        else:
            # Docker 환경: 직접 연결 시도
            final_url = get_docker_service_url()
        
        url = f"{final_url}/api/v1/tcfdreport/download/word"
        logger.info(f"최종 요청 URL: {url}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 요청 헤더에서 인증 토큰 가져오기
            auth_header = request.headers.get("Authorization")
            headers = {}
            
            if auth_header:
                headers["Authorization"] = auth_header
                logger.info(f"인증 토큰 발견: {auth_header[:20]}...")
            else:
                logger.warning("인증 토큰이 없습니다")
            
            logger.info(f"요청 데이터: {data}")
            logger.info(f"요청 헤더: {headers}")
            
            response = await client.post(
                url,
                json=data,
                headers=headers
            )
            response.raise_for_status()
            
            # 응답 헤더에서 Content-Disposition 추출
            content_disposition = response.headers.get("content-disposition", "attachment")
            content_type = response.headers.get("content-type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
            logger.info(f"Word 응답 수신 성공: {content_type}, 크기: {len(response.content)}B")
            
            # 파일 응답을 그대로 전달
            from fastapi.responses import Response
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Content-Disposition": content_disposition,
                    "Content-Length": str(len(response.content)),
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.post("/download/pdf")
async def download_tcfd_report_as_pdf(request: Request, data: dict):
    """TCFD 보고서를 PDF로 다운로드"""
    try:
        logger.info(f"TCFD Report Service - PDF 다운로드 요청 시작: {data.get('company_name', 'Unknown')}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # Docker 환경에서는 직접 연결, Railway 환경에서는 Service Discovery 사용
        if os.getenv("RAILWAY_ENVIRONMENT") == "production":
            # Railway 환경: Service Discovery에서 가져온 host 사용
            final_url = host
        else:
            # Docker 환경: 직접 연결 시도
            final_url = get_docker_service_url()
        
        url = f"{final_url}/api/v1/tcfdreport/download/pdf"
        logger.info(f"최종 요청 URL: {url}")
        logger.info(f"요청 데이터: {data}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            
            # 응답 헤더에서 Content-Disposition 추출
            content_disposition = response.headers.get("content-disposition", "attachment")
            content_type = response.headers.get("content-type", "application/pdf")
            
            logger.info(f"PDF 응답 수신 성공: {content_type}, 크기: {len(response.content)}B")
            
            # 파일 응답을 그대로 전달
            from fastapi.responses import Response
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Content-Disposition": content_disposition,
                    "Content-Length": str(len(response.content)),
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"TCFD Report Service PDF 다운로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service PDF 다운로드 실패: {str(e)}")

@router.post("/download/combined")
async def download_tcfd_report_combined(request: Request, data: dict):
    """TCFD 보고서를 Word와 PDF로 생성하여 ZIP 파일로 다운로드"""
    try:
        logger.info(f"TCFD Report Service - Combined 다운로드 요청 시작: {data.get('company_name', 'Unknown')}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # Docker 환경에서는 직접 연결, Railway 환경에서는 Service Discovery 사용
        if os.getenv("RAILWAY_ENVIRONMENT") == "production":
            # Railway 환경: Service Discovery에서 가져온 host 사용
            final_url = host
        else:
            # Docker 환경: 직접 연결 시도
            final_url = get_docker_service_url()
        
        url = f"{final_url}/api/v1/tcfdreport/download/combined"
        logger.info(f"최종 요청 URL: {url}")
        logger.info(f"요청 데이터: {data}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            
            # 응답 헤더에서 Content-Disposition 추출
            content_disposition = response.headers.get("content-disposition", "attachment")
            content_type = response.headers.get("content-type", "application/zip")
            
            logger.info(f"Combined 응답 수신 성공: {content_type}, 크기: {len(response.content)}B")
            
            # 파일 응답을 그대로 전달
            from fastapi.responses import Response
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    "Content-Disposition": content_disposition,
                    "Content-Length": str(len(response.content)),
                    "Cache-Control": "no-cache, no-store, must-revalidate",
                    "Pragma": "no-cache",
                    "Expires": "0",
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"TCFD Report Service Combined 다운로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service Combined 다운로드 실패: {str(e)}")

@router.post("/drafts")
async def create_tcfd_draft(request: Request, data: Dict[str, Any], authorization: str = Header(None)):
    """TCFD 초안 데이터 생성"""
    try:
        logger.info("🔍 TCFD 초안 데이터 생성 요청 시작")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        logger.info(f"🎯 선택된 TCFD Report Service 인스턴스: {tcfdreport_service}")
        
        if not tcfdreport_service:
            logger.error("❌ TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        logger.info(f"🔍 원본 TCFD Report Service host: {host}")
        logger.info(f"🔍 TCFD Report Service port: {port}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        
        # URL이 이미 완전한 형태인지 확인
        if host.startswith('http://') or host.startswith('https://'):
            url = f"{host}/api/v1/tcfdreport/drafts"
        else:
            # Railway/Vercel 환경에서는 환경변수에서 직접 TCFD Report Service URL 가져오기
            if os.getenv("RAILWAY_ENVIRONMENT") == "true" or os.getenv("VERCEL_ENVIRONMENT") == "true":
                railway_tcfdreport_url = os.getenv("RAILWAY_TCFDREPORT_SERVICE_URL")
                if railway_tcfdreport_url:
                    url = f"{railway_tcfdreport_url}/api/v1/tcfdreport/drafts"
                    logger.info(f"🔧 Railway/Vercel 환경에서 환경변수 TCFD Report Service URL: {url}")
                else:
                    # 환경변수가 없으면 Service Discovery에서 가져온 URL 사용
                    url = f"http://{host}:{port}/api/v1/tcfdreport/drafts"
                    logger.info(f"🔧 Railway/Vercel 환경에서 Service Discovery TCFD Report Service URL: {url}")
            else:
                # Docker 환경에서는 컨테이너 이름과 포트 사용
                url = f"http://tcfdreport-service:8004/api/v1/tcfdreport/drafts"
                logger.info(f"🔧 Docker 환경에서 TCFD Report Service URL: {url}")
        
        logger.info(f"📤 최종 요청 URL: {url}")
        
        # TCFD Report Service로 요청 전달
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=data,
                headers={"Authorization": authorization},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ TCFD 초안 데이터 생성 성공: {result}")
                return result
            else:
                logger.error(f"❌ TCFD Report Service HTTP 응답 오류: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail=f"TCFD Report Service 오류: {response.text}")
                
    except httpx.ConnectError as e:
        logger.error(f"❌ TCFD Report Service 연결 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"TCFD Report Service 연결 실패: {str(e)}")
    except Exception as e:
        logger.error(f"❌ TCFD 초안 데이터 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD 초안 데이터 생성 실패: {str(e)}")

@router.get("/drafts/{company_name}")
async def get_tcfd_drafts(request: Request, company_name: str, authorization: str = Header(None)):
    """회사별 TCFD 초안 데이터 조회"""
    try:
        logger.info(f"🔍 TCFD 초안 데이터 조회 요청 시작: {company_name}")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("❌ TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # URL 구성
        if host.startswith('http://') or host.startswith('https://'):
            url = f"{host}/api/v1/tcfdreport/drafts/{company_name}"
        else:
            if os.getenv("RAILWAY_ENVIRONMENT") == "true" or os.getenv("VERCEL_ENVIRONMENT") == "true":
                railway_tcfdreport_url = os.getenv("RAILWAY_TCFDREPORT_SERVICE_URL")
                if railway_tcfdreport_url:
                    url = f"{railway_tcfdreport_url}/api/v1/tcfdreport/drafts/{company_name}"
                else:
                    url = f"http://{host}:{port}/api/v1/tcfdreport/drafts/{company_name}"
            else:
                url = f"http://tcfdreport-service:8004/api/v1/tcfdreport/drafts/{company_name}"
        
        logger.info(f"📤 최종 요청 URL: {url}")
        
        # TCFD Report Service로 요청 전달
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": authorization},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ TCFD 초안 데이터 조회 성공: {result}")
                return result
            else:
                logger.error(f"❌ TCFD Report Service HTTP 응답 오류: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail=f"TCFD Report Service 오류: {response.text}")
                
    except httpx.ConnectError as e:
        logger.error(f"❌ TCFD Report Service 연결 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"TCFD Report Service 연결 실패: {str(e)}")
    except Exception as e:
        logger.error(f"❌ TCFD 초안 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD 초안 데이터 조회 실패: {str(e)}")

@router.get("/drafts/id/{draft_id}")
async def get_tcfd_draft_by_id(request: Request, draft_id: int, authorization: str = Header(None)):
    """ID로 TCFD 초안 데이터 조회"""
    try:
        logger.info(f"🔍 TCFD 초안 데이터 ID 조회 요청 시작: {draft_id}")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("❌ TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # URL 구성
        if host.startswith('http://') or host.startswith('https://'):
            url = f"{host}/api/v1/tcfdreport/drafts/id/{draft_id}"
        else:
            if os.getenv("RAILWAY_ENVIRONMENT") == "true" or os.getenv("VERCEL_ENVIRONMENT") == "true":
                railway_tcfdreport_url = os.getenv("RAILWAY_TCFDREPORT_SERVICE_URL")
                if railway_tcfdreport_url:
                    url = f"{railway_tcfdreport_url}/api/v1/tcfdreport/drafts/id/{draft_id}"
                else:
                    url = f"http://{host}:{port}/api/v1/tcfdreport/drafts/id/{draft_id}"
            else:
                url = f"http://tcfdreport-service:8004/api/v1/tcfdreport/drafts/id/{draft_id}"
        
        logger.info(f"📤 최종 요청 URL: {url}")
        
        # TCFD Report Service로 요청 전달
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={"Authorization": authorization},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ TCFD 초안 데이터 ID 조회 성공: {result}")
                return result
            else:
                logger.error(f"❌ TCFD Report Service HTTP 응답 오류: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail=f"TCFD Report Service 오류: {response.text}")
                
    except httpx.ConnectError as e:
        logger.error(f"❌ TCFD Report Service 연결 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"TCFD Report Service 연결 실패: {str(e)}")
    except Exception as e:
        logger.error(f"❌ TCFD 초안 데이터 ID 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD 초안 데이터 ID 조회 실패: {str(e)}")

@router.put("/drafts/{draft_id}/status")
async def update_draft_status(request: Request, draft_id: int, status_data: dict, authorization: str = Header(None)):
    """TCFD 초안 데이터 상태 업데이트"""
    try:
        status = status_data.get("status")
        if not status:
            raise HTTPException(status_code=400, detail="status 필드가 필요합니다")
        
        logger.info(f"🔍 TCFD 초안 데이터 상태 업데이트 요청 시작: {draft_id} -> {status}")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("❌ TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # URL 구성
        if host.startswith('http://') or host.startswith('https://'):
            url = f"{host}/api/v1/tcfdreport/drafts/{draft_id}/status"
        else:
            if os.getenv("RAILWAY_ENVIRONMENT") == "true" or os.getenv("VERCEL_ENVIRONMENT") == "true":
                railway_tcfdreport_url = os.getenv("RAILWAY_TCFDREPORT_SERVICE_URL")
                if railway_tcfdreport_url:
                    url = f"{railway_tcfdreport_url}/api/v1/tcfdreport/drafts/{draft_id}/status"
                else:
                    url = f"http://{host}:{port}/api/v1/tcfdreport/drafts/{draft_id}/status"
            else:
                url = f"http://tcfdreport-service:8004/api/v1/tcfdreport/drafts/{draft_id}/status"
        
        logger.info(f"📤 최종 요청 URL: {url}")
        
        # TCFD Report Service로 요청 전달
        async with httpx.AsyncClient() as client:
            response = await client.put(
                url,
                json={"status": status},
                headers={"Authorization": authorization},
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ TCFD 초안 데이터 상태 업데이트 성공: {result}")
                return result
            else:
                logger.error(f"❌ TCFD Report Service HTTP 응답 오류: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail=f"TCFD Report Service 오류: {response.text}")
                
    except httpx.ConnectError as e:
        logger.error(f"❌ TCFD Report Service 연결 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"TCFD Report Service 연결 실패: {str(e)}")
    except Exception as e:
        logger.error(f"❌ TCFD 초안 데이터 상태 업데이트 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD 초안 데이터 상태 업데이트 실패: {str(e)}")
