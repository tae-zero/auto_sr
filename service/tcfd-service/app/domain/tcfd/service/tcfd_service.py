"""
TCFD Service TCFD 서비스
- TCFD 비즈니스 로직 처리
- AI 분석, 위험 평가, 보고서 생성
- 기존 서비스들의 기능 통합
"""
from typing import Dict, Any, Optional, List
import logging
from fastapi import UploadFile, HTTPException

from app.domain.tcfd.repository.tcfd_repository import TCFDRepository
from app.domain.tcfd.model.tcfd_model import (
    CompanyInfoRequest, FinancialDataRequest, RiskAssessmentRequest
)
from app.domain.tcfd.entity.tcfd_entity import TCFDEntity, ClimateRiskEntity
from app.domain.tcfd.schema.tcfd_schema import TCFDReport, ClimateRisk

logger = logging.getLogger(__name__)

class TCFDService:
    def __init__(self):
        self.repository = TCFDRepository()
        # AI 서비스들은 비활성화 (사용하지 않음)
        # self.analysis_service = None
        # self.report_service = None
        # self.risk_assessment_service = None
    
    async def get_company_financial_data(self, company_name: str) -> Dict[str, Any]:
        """특정 회사의 재무정보 조회"""
        try:
            result = await self.repository.get_company_financial_data(company_name)
            # Repository에서 이미 success 필드를 포함하여 반환하므로 그대로 전달
            return result
            
        except Exception as e:
            logger.error(f"회사별 재무정보 조회 실패: {str(e)}")
            raise Exception(f"재무정보 조회 실패: {str(e)}")
    
    async def get_company_financial_summary(self, company_name: str) -> Dict[str, Any]:
        """특정 회사의 재무요약 정보 조회"""
        try:
            result = await self.repository.get_company_financial_summary(company_name)
            return {
                "success": True,
                "company_name": company_name,
                "summary": result,
                "message": f"{company_name}의 재무요약 조회 완료"
            }
            
        except Exception as e:
            logger.error(f"회사별 재무요약 조회 실패: {str(e)}")
            raise Exception(f"재무요약 조회 실패: {str(e)}")
    
    async def get_all_companies(self) -> Dict[str, Any]:
        """등록된 모든 회사 목록 조회"""
        try:
            result = await self.repository.get_all_companies()
            return {
                "success": True,
                "companies": result,
                "total_count": len(result),
                "message": "회사 목록 조회 완료"
            }
            
        except Exception as e:
            logger.error(f"회사 목록 조회 실패: {str(e)}")
            raise Exception(f"회사 목록 조회 실패: {str(e)}")
    
    async def analyze_report(self, file: UploadFile, company_info: Dict[str, Any]) -> Dict[str, Any]:
        """TCFD 보고서 AI 분석 (비활성화)"""
        return {
            "success": False,
            "message": "AI 분석 기능은 현재 비활성화되어 있습니다",
            "data": None
        }
    
    async def assess_climate_risk(
        self, 
        company_request: CompanyInfoRequest, 
        financial_request: FinancialDataRequest
    ) -> Dict[str, Any]:
        """TCFD 위험 평가 (비활성화)"""
        return {
            "success": False,
            "message": "AI 위험 평가 기능은 현재 비활성화되어 있습니다",
            "data": None
        }
    
    async def generate_report(
        self, 
        company_request: CompanyInfoRequest, 
        financial_request: FinancialDataRequest,
        risk_request: RiskAssessmentRequest
    ) -> Dict[str, Any]:
        """TCFD 보고서 생성 (비활성화)"""
        return {
            "success": False,
            "message": "AI 보고서 생성 기능은 현재 비활성화되어 있습니다",
            "data": None
        }
    
    async def get_financial_data(self) -> Dict[str, Any]:
        """재무 데이터 조회"""
        try:
            # 5개 테이블의 재무 데이터 조회
            result = await self.repository.get_all_financial_data()
            return {
                "success": True,
                "data": result,
                "message": "재무 데이터 조회 완료"
            }
            
        except Exception as e:
            logger.error(f"재무 데이터 조회 실패: {str(e)}")
            raise Exception(f"재무 데이터 조회 실패: {str(e)}")
    
    async def create_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """재무 데이터 생성"""
        try:
            # 데이터 검증 및 저장
            result = await self.repository.create_financial_data(data)
            return {
                "success": True,
                "data": result,
                "message": "재무 데이터 생성 완료"
            }
            
        except Exception as e:
            logger.error(f"재무 데이터 생성 실패: {str(e)}")
            raise Exception(f"재무 데이터 생성 실패: {str(e)}")
    
    async def get_climate_scenarios(self) -> Dict[str, Any]:
        """기후 시나리오 조회"""
        try:
            # 기후 시나리오 데이터 조회
            result = await self.repository.get_climate_scenarios()
            return {
                "success": True,
                "data": result,
                "message": "기후 시나리오 조회 완료"
            }
            
        except Exception as e:
            logger.error(f"기후 시나리오 조회 실패: {str(e)}")
            raise Exception(f"기후 시나리오 조회 실패: {str(e)}")
    
    async def close(self):
        """리소스 정리"""
        await self.repository.close()
