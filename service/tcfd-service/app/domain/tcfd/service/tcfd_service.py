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
        # 기존 서비스들 초기화
        from app.domain.tcfd.analysis_service import TCFDAnalysisService
        from app.domain.tcfd.report_service import TCFDReportService
        from app.domain.tcfd.risk_assessment_service import RiskAssessmentService
        
        self.analysis_service = TCFDAnalysisService()
        self.report_service = TCFDReportService()
        self.risk_assessment_service = RiskAssessmentService()
    
    async def analyze_report(self, file: UploadFile, company_info: Dict[str, Any]) -> Dict[str, Any]:
        """TCFD 보고서 AI 분석"""
        try:
            # 파일 검증
            if not file.filename or not file.filename.endswith(('.pdf', '.docx', '.txt')):
                raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다")
            
            # AI 분석 서비스 호출
            result = await self.analysis_service.analyze_report(file, company_info)
            
            # 분석 결과 저장
            analysis_entity = TCFDEntity(
                company_info=company_info,
                analysis_result=result,
                status="completed"
            )
            await self.repository.save_analysis_result(analysis_entity)
            
            return {
                "success": True,
                "data": result,
                "message": "TCFD 보고서 분석 완료"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"TCFD 보고서 분석 실패: {str(e)}")
            raise Exception(f"분석 처리 실패: {str(e)}")
    
    async def assess_climate_risk(
        self, 
        company_request: CompanyInfoRequest, 
        financial_request: FinancialDataRequest
    ) -> Dict[str, Any]:
        """TCFD 위험 평가"""
        try:
            # 위험 평가 서비스 호출
            result = await self.risk_assessment_service.assess_climate_risk(
                company_info=company_request.dict(),
                financial_data=financial_request.dict()
            )
            
            # 위험 평가 결과 저장
            risk_entity = ClimateRiskEntity(
                company_info=company_request.dict(),
                financial_data=financial_request.dict(),
                risk_assessment=result,
                status="completed"
            )
            await self.repository.save_risk_assessment(risk_entity)
            
            return {
                "success": True,
                "data": result,
                "message": "TCFD 위험 평가 완료"
            }
            
        except Exception as e:
            logger.error(f"TCFD 위험 평가 실패: {str(e)}")
            raise Exception(f"위험 평가 처리 실패: {str(e)}")
    
    async def generate_report(
        self, 
        company_request: CompanyInfoRequest, 
        financial_request: FinancialDataRequest,
        risk_request: RiskAssessmentRequest
    ) -> Dict[str, Any]:
        """TCFD 보고서 생성"""
        try:
            # 보고서 생성 서비스 호출
            result = await self.report_service.generate_report(
                company_info=company_request.dict(),
                financial_data=financial_request.dict(),
                risk_assessment=risk_request.dict()
            )
            
            # 보고서 결과 저장
            report_entity = TCFDEntity(
                company_info=company_request.dict(),
                financial_data=financial_request.dict(),
                risk_assessment=risk_request.dict(),
                report_result=result,
                status="completed"
            )
            await self.repository.save_report_result(report_entity)
            
            return {
                "success": True,
                "data": result,
                "message": "TCFD 보고서 생성 완료"
            }
            
        except Exception as e:
            logger.error(f"TCFD 보고서 생성 실패: {str(e)}")
            raise Exception(f"보고서 생성 처리 실패: {str(e)}")
    
    async def get_financial_data(self) -> Dict[str, Any]:
        """재무 데이터 조회"""
        try:
            # 6개 테이블의 재무 데이터 조회
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
