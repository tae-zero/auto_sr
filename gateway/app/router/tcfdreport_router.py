from fastapi import APIRouter, Request, HTTPException
from app.domain.discovery.service_discovery import ServiceDiscovery
import httpx
import logging
import traceback
import os

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

@router.get("/health")
async def health_check(request: Request):
    """TCFD Report Service 헬스 체크"""
    try:
        logger.info("🔍 TCFD Report Service 헬스 체크 요청 시작")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("❌ TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                host = f"https://{host}"
            else:
                host = f"http://{host}:{port}"
        
        logger.info(f"🌐 TCFD Report Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/health")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{host}/health")
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Report Service 헬스 체크 성공: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.get("/company-financial-data")
async def get_company_financial_data(request: Request, company_name: str):
    """회사별 재무정보 조회 (TCFD Report Service)"""
    try:
        logger.info(f"🔍 TCFD Report Service - 회사별 재무정보 조회 요청 시작: {company_name}")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("❌ TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                host = f"https://{host}"
            else:
                host = f"http://{host}:{port}"
        
        logger.info(f"🌐 TCFD Report Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfdreport/company-financial-data")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{host}/api/v1/tcfdreport/company-financial-data",
                params={"company_name": company_name}
            )
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Report Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.get("/standards")
async def get_tcfd_standards(request: Request):
    """TCFD 표준 정보 조회 (TCFD Report Service)"""
    try:
        logger.info("🔍 TCFD Report Service - TCFD 표준 정보 조회 요청 시작")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("❌ TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                host = f"https://{host}"
            else:
                host = f"http://{host}:{port}"
        
        logger.info(f"🌐 TCFD Report Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfdreport/standards")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{host}/api/v1/tcfdreport/standards")
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Report Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.post("/inputs")
async def create_tcfd_input(request: Request, data: dict):
    """TCFD 입력 데이터 생성"""
    try:
        logger.info("🔍 TCFD Report Service - TCFD 입력 데이터 생성 요청 시작")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("❌ TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                host = f"https://{host}"
            else:
                host = f"http://{host}:{port}"
        
        logger.info(f"🌐 TCFD Report Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfdreport/inputs")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 요청 헤더에서 인증 토큰 가져오기
            auth_header = request.headers.get("Authorization")
            headers = {}
            
            if auth_header:
                headers["Authorization"] = auth_header
                logger.info(f"🔐 인증 토큰 발견: {auth_header[:20]}...")
            else:
                logger.warning("⚠️ 인증 토큰이 없습니다")
            
            logger.info(f"📤 요청 데이터: {data}")
            logger.info(f"📤 요청 헤더: {headers}")
            
            # Docker 환경에서는 직접 연결, Railway 환경에서는 Service Discovery 사용
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                final_url = TCFD_REPORT_SERVICE_URL
            else:
                # Docker 환경: 직접 연결 시도
                final_url = get_docker_service_url()
            
            url = f"{final_url}/api/v1/tcfdreport/inputs"
            logger.info(f"📤 최종 요청 URL: {url}")
            
            response = await client.post(
                url,
                json=data,
                headers=headers
            )
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Report Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")

@router.get("/inputs")
async def get_tcfd_inputs(request: Request):
    """TCFD 입력 데이터 조회"""
    try:
        logger.info("🔍 TCFD Report Service - TCFD 입력 데이터 조회 요청 시작")
        
        # Service Discovery를 통해 TCFD Report Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfdreport_service = service_discovery.get_service_instance("tcfdreport-service")
        
        if not tcfdreport_service:
            logger.error("❌ TCFD Report Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Report Service를 찾을 수 없습니다")
        
        # TCFD Report Service로 요청 전달
        host = tcfdreport_service.host
        port = tcfdreport_service.port
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                host = f"https://{host}"
            else:
                host = f"http://{host}:{port}"
        
        logger.info(f"🌐 TCFD Report Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/inputs")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{host}/api/v1/tcfd/inputs")
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Report Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Report Service HTTP 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Report Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Report Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TCFD Report Service 요청 실패: {str(e)}")
