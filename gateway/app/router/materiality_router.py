from fastapi import APIRouter, Request, HTTPException
from app.domain.discovery.service_discovery import ServiceDiscovery
from app.domain.discovery.service_type import ServiceType
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/api/v1/materiality/data/{path:path}")
async def materiality_proxy(request: Request, path: str):
    """Materiality Service로 요청을 전달하는 프록시"""
    try:
        # 서비스 디스커버리에서 Materiality Service 정보 가져오기
        service_discovery = request.app.state.service_discovery
        materiality_service = service_discovery.get_service(ServiceType.MATERIALITY)
        
        if not materiality_service:
            raise HTTPException(status_code=503, detail="Materiality Service를 찾을 수 없습니다")
        
        # Materiality Service로 요청 전달
        service_url = f"https://{materiality_service['host']}/api/v1/materiality/data/{path}"
        
        logger.info(f"Materiality Service로 요청 전달: {service_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(service_url)
            return response.json()
            
    except Exception as e:
        logger.error(f"Materiality Service 프록시 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Materiality Service 요청 실패: {str(e)}")

@router.get("/api/v1/materiality/{path:path}")
async def materiality_general_proxy(request: Request, path: str):
    """Materiality Service의 일반 엔드포인트로 요청을 전달하는 프록시"""
    try:
        # 서비스 디스커버리에서 Materiality Service 정보 가져오기
        service_discovery = request.app.state.service_discovery
        materiality_service = service_discovery.get_service(ServiceType.MATERIALITY)
        
        if not materiality_service:
            raise HTTPException(status_code=503, detail="Materiality Service를 찾을 수 없습니다")
        
        # Materiality Service로 요청 전달
        service_url = f"https://{materiality_service['host']}/api/v1/materiality/{path}"
        
        logger.info(f"Materiality Service로 요청 전달: {service_url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(service_url)
            return response.json()
            
    except Exception as e:
        logger.error(f"Materiality Service 프록시 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Materiality Service 요청 실패: {str(e)}")
