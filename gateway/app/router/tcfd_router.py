from fastapi import APIRouter, Request, HTTPException
from app.domain.discovery.service_discovery import ServiceDiscovery
import httpx
import logging
import traceback
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tcfd", tags=["tcfd"])

@router.get("/companies")
async def get_companies(request: Request):
    """회사 목록 조회"""
    try:
        logger.info("🔍 회사 목록 조회 요청 시작")
        
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        tcfd_service = service_discovery.get_service_instance("tcfd-service")
        logger.info(f"🎯 TCFD Service 인스턴스: {tcfd_service}")
        
        if not tcfd_service:
            logger.error("❌ TCFD Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service.host
        logger.info(f"🔍 원본 TCFD Service host: {host}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            # Docker 환경에서는 http:// 사용, Railway에서는 https:// 사용
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                host = f"https://{host}"
                logger.info(f"🔧 Railway 환경: https:// 추가됨")
            else:
                host = f"http://{host}"
                logger.info(f"🔧 Docker 환경: http:// 추가됨")
        
        logger.info(f"🌐 TCFD Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/companies")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{host}/api/v1/tcfd/companies")
            logger.info(f"📥 TCFD Service 응답 상태: {response.status_code}")
            logger.info(f"📥 TCFD Service 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Service 요청 실패: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"TCFD Service 요청 실패: {str(e)}")

@router.get("/company-financial-data")
async def get_company_financial_data(request: Request, company_name: str):
    """회사별 재무정보 조회"""
    try:
        logger.info(f"🔍 회사별 재무정보 조회 요청 시작: {company_name}")
        
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        tcfd_service = service_discovery.get_service_instance("tcfd-service")
        logger.info(f"🎯 TCFD Service 인스턴스: {tcfd_service}")
        
        if not tcfd_service:
            logger.error("❌ TCFD Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service.host
        logger.info(f"🔍 원본 TCFD Service host: {host}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            # Docker 환경에서는 http:// 사용, Railway에서는 https:// 사용
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                host = f"https://{host}"
                logger.info(f"🔧 Railway 환경: https:// 추가됨")
            else:
                host = f"http://{host}"
                logger.info(f"🔧 Docker 환경: http:// 추가됨")
        
        logger.info(f"🌐 TCFD Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/company-financial-data")
        logger.info(f"📤 요청 파라미터: company_name={company_name}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{host}/api/v1/tcfd/company-financial-data",
                params={"company_name": company_name}
            )
            logger.info(f"📥 TCFD Service 응답 상태: {response.status_code}")
            logger.info(f"📥 TCFD Service 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Service 응답 데이터: {response_data}")
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Service 요청 실패: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"TCFD Service 요청 실패: {str(e)}")
