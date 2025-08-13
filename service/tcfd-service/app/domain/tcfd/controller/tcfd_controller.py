"""
TCFD Service TCFD 컨트롤러
- TCFD 관련 API 엔드포인트
- 요청/응답 처리 및 검증
- AI 분석, 위험 평가, 보고서 생성
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from typing import Dict, Any, Optional
import logging
import json

from app.domain.tcfd.service.tcfd_service import TCFDService
from app.domain.tcfd.model.tcfd_model import (
    CompanyInfoRequest, FinancialDataRequest, RiskAssessmentRequest,
    TCFDAnalysisResponse, RiskAssessmentResponse, ReportGenerationResponse
)
from app.domain.tcfd.schema.tcfd_schema import TCFDReport, ClimateRisk

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tcfd", tags=["TCFD"])

@router.get("/health")
async def health_check():
    """TCFD Service 상태 확인"""
    return {
        "status": "healthy",
        "service": "tcfd-service",
        "architecture": "MSV Pattern with Layered Architecture",
        "layers": [
            "Controller Layer - TCFD API 엔드포인트",
            "Service Layer - TCFD 비즈니스 로직",
            "Repository Layer - 데이터 접근",
            "Entity Layer - 데이터베이스 엔티티",
            "Model Layer - Pydantic 모델",
            "Schema Layer - TCFD 스키마"
        ]
    }

@router.get("/financial-data/company/{company_name}")
async def get_company_financial_data(company_name: str):
    """특정 회사의 재무정보 조회"""
    try:
        tcfd_service = TCFDService()
        result = await tcfd_service.get_company_financial_data(company_name)
        return result
        
    except Exception as e:
        logger.error(f"회사별 재무정보 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financial-data/company/{company_name}/summary")
async def get_company_financial_summary(company_name: str):
    """특정 회사의 재무요약 정보 조회"""
    try:
        tcfd_service = TCFDService()
        result = await tcfd_service.get_company_financial_summary(company_name)
        return result
        
    except Exception as e:
        logger.error(f"회사별 재무요약 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies")
async def get_all_companies():
    """등록된 모든 회사 목록 조회"""
    try:
        tcfd_service = TCFDService()
        result = await tcfd_service.get_all_companies()
        return result
        
    except Exception as e:
        logger.error(f"회사 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-report", response_model=TCFDAnalysisResponse)
async def analyze_tcfd_report(
    file: UploadFile = File(...),
    company_info: Optional[str] = Form("{}")
):
    """TCFD 보고서 AI 분석"""
    try:
        company_data = json.loads(company_info) if company_info else {}
        
        tcfd_service = TCFDService()
        result = await tcfd_service.analyze_report(file, company_data)
        
        return TCFDAnalysisResponse(**result)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="잘못된 JSON 형식입니다")
    except Exception as e:
        logger.error(f"TCFD 보고서 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk-assessment", response_model=RiskAssessmentResponse)
async def assess_tcfd_risk(
    company_info: str = Form(...),
    financial_data: str = Form(...)
):
    """TCFD 위험 평가"""
    try:
        company_data = json.loads(company_info)
        financial_info = json.loads(financial_data)
        
        # 요청 데이터 검증
        company_request = CompanyInfoRequest(**company_data)
        financial_request = FinancialDataRequest(**financial_info)
        
        tcfd_service = TCFDService()
        result = await tcfd_service.assess_climate_risk(
            company_request, financial_request
        )
        
        return RiskAssessmentResponse(**result)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="잘못된 JSON 형식입니다")
    except Exception as e:
        logger.error(f"TCFD 위험 평가 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-report", response_model=ReportGenerationResponse)
async def generate_tcfd_report(
    company_info: str = Form(...),
    financial_data: str = Form(...),
    risk_assessment: str = Form(...)
):
    """TCFD 보고서 생성"""
    try:
        company_data = json.loads(company_info)
        financial_info = json.loads(financial_data)
        risk_info = json.loads(risk_assessment)
        
        # 요청 데이터 검증
        company_request = CompanyInfoRequest(**company_data)
        financial_request = FinancialDataRequest(**financial_info)
        risk_request = RiskAssessmentRequest(**risk_info)
        
        tcfd_service = TCFDService()
        result = await tcfd_service.generate_report(
            company_request, financial_request, risk_request
        )
        
        return ReportGenerationResponse(**result)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="잘못된 JSON 형식입니다")
    except Exception as e:
        logger.error(f"TCFD 보고서 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/financial-data", response_model=Dict[str, Any])
async def get_financial_data():
    """재무 데이터 조회"""
    try:
        tcfd_service = TCFDService()
        result = await tcfd_service.get_financial_data()
        return result
        
    except Exception as e:
        logger.error(f"재무 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/financial-data")
async def create_financial_data(data: Dict[str, Any]):
    """재무 데이터 생성"""
    try:
        tcfd_service = TCFDService()
        result = await tcfd_service.create_financial_data(data)
        return result
        
    except Exception as e:
        logger.error(f"재무 데이터 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/climate-scenarios", response_model=Dict[str, Any])
async def get_climate_scenarios():
    """기후 시나리오 조회"""
    try:
        tcfd_service = TCFDService()
        result = await tcfd_service.get_climate_scenarios()
        return result
        
    except Exception as e:
        logger.error(f"기후 시나리오 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
