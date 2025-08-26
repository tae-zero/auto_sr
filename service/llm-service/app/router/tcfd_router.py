from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any
import logging

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

@tcfd_router.get("/health")
async def health_check():
    """TCFD 서비스 상태 확인"""
    return {"status": "healthy", "service": "TCFD Report Service"}
