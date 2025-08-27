from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any
import logging
import httpx
import os

from ..domain.tcfd.tcfd_report_service import TCFDReportService
from ..domain.tcfd.tcfd_model import TCFDReportRequest, TCFDReportResponse, TCFDRecommendationRequest, TCFDRecommendationResponse
from ..www.jwt_auth_middleware import verify_token

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT 인증
security = HTTPBearer()

# TCFD 라우터 생성
tcfd_router = APIRouter(
    prefix="/tcfd",
    tags=["TCFD"],
    dependencies=[Depends(verify_token)]
)

# TCFD 보고서 서비스 인스턴스
tcfd_service = TCFDReportService()

@tcfd_router.post("/generate-report", response_model=TCFDReportResponse)
async def generate_tcfd_report(request: TCFDReportRequest):
    """
    TCFD 권고사항 데이터를 기반으로 보고서 생성
    
    Args:
        request: TCFD 보고서 생성 요청 데이터
        
    Returns:
        TCFDReportResponse: 생성된 보고서 내용
    """
    try:
        logger.info(f"TCFD 보고서 생성 요청: {request.company_name}, {request.report_year}")
        
        # TCFD 보고서 생성
        response = tcfd_service.generate_tcfd_report(request)
        
        if response.success:
            logger.info(f"TCFD 보고서 생성 성공: {request.company_name}")
            return response
        else:
            logger.error(f"TCFD 보고서 생성 실패: {response.error_message}")
            raise HTTPException(
                status_code=500,
                detail=f"보고서 생성 중 오류가 발생했습니다: {response.error_message}"
            )
            
    except Exception as e:
        logger.error(f"TCFD 보고서 생성 중 예외 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}"
        )

@tcfd_router.post("/generate-recommendation", response_model=TCFDRecommendationResponse)
async def generate_tcfd_recommendation(request: TCFDRecommendationRequest):
    """
    특정 TCFD 권고사항에 대한 문장 생성
    
    Args:
        request: TCFD 권고사항 문장 생성 요청 데이터
        
    Returns:
        TCFDRecommendationResponse: 생성된 권고사항 문장
    """
    try:
        logger.info(f"TCFD 권고사항 문장 생성 요청: {request.recommendation_type}, {request.llm_provider}")
        
        # TCFD 권고사항 문장 생성
        response = tcfd_service.generate_tcfd_recommendation(request)
        
        if response.success:
            logger.info(f"TCFD 권고사항 문장 생성 성공: {request.recommendation_type}")
            return response
        else:
            logger.error(f"TCFD 권고사항 문장 생성 실패: {response.error_message}")
            raise HTTPException(
                status_code=500,
                detail=f"권고사항 문장 생성 중 오류가 발생했습니다: {response.error_message}"
            )
            
    except Exception as e:
        logger.error(f"TCFD 권고사항 문장 생성 중 예외 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"권고사항 문장 생성 중 오류가 발생했습니다: {str(e)}"
        )

@tcfd_router.get("/inputs")
async def get_tcfd_inputs():
    """
    TCFD 입력 데이터 조회 (tcfd-service로 요청 전달)
    
    Returns:
        Dict: TCFD 입력 데이터 목록
    """
    try:
        logger.info("🔍 TCFD 입력 데이터 조회 요청 시작")
        
        # tcfd-service URL 결정 (환경별 처리)
        tcfd_service_url = os.getenv("TCFD_SERVICE_URL")
        if tcfd_service_url:
            url = f"{tcfd_service_url}/api/v1/tcfd/inputs"
        else:
            # 환경변수가 없으면 localhost 사용 (개발 환경)
            url = "http://localhost:8005/api/v1/tcfd/inputs"
        
        logger.info(f"📤 TCFD Service 요청 URL: {url}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            logger.info(f"📥 TCFD Service 응답 상태: {response.status_code}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Service 응답 데이터 조회 성공")
            
            return response_data
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code, 
            detail=f"TCFD Service 응답 오류: {e.response.status_code}"
        )
    except Exception as e:
        logger.error(f"❌ TCFD 입력 데이터 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"TCFD 입력 데이터 조회 실패: {str(e)}"
        )

@tcfd_router.get("/health")
async def health_check():
    """TCFD 서비스 상태 확인"""
    return {"status": "healthy", "service": "TCFD Report Service"}
