from fastapi import APIRouter, Request, HTTPException
from app.domain.discovery.service_discovery import ServiceDiscovery
import httpx
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tcfd", tags=["tcfd"])

@router.get("/companies")
async def get_companies(request: Request):
    """회사 목록 조회"""
    try:
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfd_service = service_discovery.get_service("tcfd-service")
        
        if not tcfd_service:
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service['host']
        if not host.startswith('http'):
            host = f"https://{host}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{host}/api/v1/tcfd/companies")
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Service 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="TCFD Service 응답 오류")
    except Exception as e:
        logger.error(f"TCFD Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="TCFD Service 요청 실패")

@router.get("/company-financial-data")
async def get_company_financial_data(request: Request, company_name: str):
    """회사별 재무정보 조회"""
    try:
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        tcfd_service = service_discovery.get_service("tcfd-service")
        
        if not tcfd_service:
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service['host']
        if not host.startswith('http'):
            host = f"https://{host}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{host}/api/v1/tcfd/company-financial-data",
                params={"company_name": company_name}
            )
            response.raise_for_status()
            return response.json()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"TCFD Service 응답 오류: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail="TCFD Service 응답 오류")
    except Exception as e:
        logger.error(f"TCFD Service 요청 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="TCFD Service 요청 실패")
