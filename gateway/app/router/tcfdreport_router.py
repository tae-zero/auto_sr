from fastapi import APIRouter, Request, HTTPException
from app.domain.discovery.service_discovery import ServiceDiscovery
import httpx
import logging
import traceback
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tcfdreport", tags=["tcfdreport"])

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
                host = f"http://{host}"
        
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
                host = f"http://{host}"
        
        logger.info(f"🌐 TCFD Report Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/company-financial-data")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{host}/api/v1/tcfd/company-financial-data",
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
                host = f"http://{host}"
        
        logger.info(f"🌐 TCFD Report Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/standards")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(f"{host}/api/v1/tcfd/standards")
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
                host = f"http://{host}"
        
        logger.info(f"🌐 TCFD Report Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/inputs")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(f"{host}/api/v1/tcfd/inputs", json=data)
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
                host = f"http://{host}"
        
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
