"""
TCFD Service TCFD 서비스
- TCFD 비즈니스 로직 처리
- AI 분석, 위험 평가, 보고서 생성
- 기존 서비스들의 기능 통합
"""
from typing import Dict, Any, Optional, List
import logging
import os
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.tcfd.repository.tcfd_repository import TCFDRepository
from app.domain.tcfd.model.tcfd_model import (
    CompanyInfoRequest, FinancialDataRequest, RiskAssessmentRequest
)
from app.domain.tcfd.entity.tcfd_entity import TCFDEntity, ClimateRiskEntity
from app.domain.tcfd.schema.tcfd_schema import TCFDReport, ClimateRisk
from app.common.models import TCFDStandard

logger = logging.getLogger(__name__)

class TCFDService:
    def __init__(self):
        self.repository = TCFDRepository()
        # AI 서비스들은 비활성화 (사용하지 않음)
        # self.analysis_service = None
        # self.report_service = None
        # self.risk_assessment_service = None
    
    # TCFD 표준 정보 조회 메서드 (환경별 처리)
    async def get_tcfd_standards(self, db) -> List[TCFDStandard]:
        """TCFD 표준 정보 전체 조회"""
        if os.getenv("RAILWAY_ENVIRONMENT") == "true":
            # Railway 환경: 비동기 처리
            result = await db.execute(select(TCFDStandard))
            return result.scalars().all()
        else:
            # Docker 환경: 동기 처리
            from sqlalchemy.orm import Session
            if isinstance(db, Session):
                result = db.execute(select(TCFDStandard))
                return result.scalars().all()
            else:
                # 비동기 세션인 경우
                result = await db.execute(select(TCFDStandard))
                return result.scalars().all()
    
    async def get_tcfd_standards_by_category(self, db, category: str) -> List[TCFDStandard]:
        """카테고리별 TCFD 표준 정보 조회"""
        if os.getenv("RAILWAY_ENVIRONMENT") == "true":
            # Railway 환경: 비동기 처리
            result = await db.execute(select(TCFDStandard).where(TCFDStandard.category == category))
            return result.scalars().all()
        else:
            # Docker 환경: 동기 처리
            from sqlalchemy.orm import Session
            if isinstance(db, Session):
                result = db.execute(select(TCFDStandard).where(TCFDStandard.category == category))
                return result.scalars().all()
            else:
                # 비동기 세션인 경우
                result = await db.execute(select(TCFDStandard).where(TCFDStandard.category == category))
                return result.scalars().all()
    
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
    
    async def get_company_overview(self, company_name: str) -> Optional[Dict]:
        """회사별 기업개요 정보 조회"""
        try:
            logger.info(f"🔍 기업개요 정보 조회 시작: {company_name}")
            
            # PostgreSQL 데이터베이스 연결 (asyncpg 직접 사용)
            import asyncpg
            import os
            
            # Railway 환경변수에서 데이터베이스 URL 가져오기
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                logger.error("❌ DATABASE_URL 환경변수가 설정되지 않았습니다")
                return None
            
            # asyncpg는 postgresql:// 또는 postgres:// 스키마만 지원
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            # asyncpg로 직접 연결
            conn = await asyncpg.connect(database_url)
            
            try:
                # 회사명으로 기업개요 정보 조회 (부분 일치)
                query = """
                    SELECT 종목코드, 종목명, 주소, 설립일, 대표자, 전화번호, 홈페이지
                    FROM corporation_overview 
                    WHERE LOWER(종목명) LIKE LOWER($1) 
                    OR LOWER(종목명) LIKE LOWER($2)
                    LIMIT 1
                """
                
                result = await conn.fetchrow(query, f"%{company_name}%", f"{company_name}%")
                
                if result:
                    overview = {
                        "종목코드": result[0],
                        "종목명": result[1],
                        "주소": result[2],
                        "설립일": result[3].isoformat() if result[3] else None,
                        "대표자": result[4],
                        "전화번호": result[5],
                        "홈페이지": result[6]
                    }
                    
                    logger.info(f"✅ 기업개요 정보 조회 성공: {overview['종목명']}")
                    return overview
                else:
                    logger.warning(f"⚠️ 기업개요 정보를 찾을 수 없음: {company_name}")
                    return None
                    
            finally:
                await conn.close()
                
        except Exception as e:
            logger.error(f"❌ 기업개요 정보 조회 실패: {str(e)}")
            raise
    
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
    
    async def get_climate_scenarios(
        self, 
        scenario_code: Optional[str] = None,
        variable_code: Optional[str] = None,
        year: Optional[int] = None,
        current_user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """기후 시나리오 데이터 조회"""
        try:
            # 데이터베이스에서 기후 데이터 조회
            result = await self.repository.get_climate_scenarios(
                scenario_code=scenario_code,
                variable_code=variable_code,
                year=year
            )
            
            return {
                "success": True,
                "data": result,
                "filters": {
                    "scenario_code": scenario_code,
                    "variable_code": variable_code,
                    "year": year
                },
                "message": "기후 시나리오 데이터 조회 완료"
            }
            
        except Exception as e:
            logger.error(f"기후 시나리오 데이터 조회 실패: {str(e)}")
            raise Exception(f"기후 시나리오 데이터 조회 실패: {str(e)}")
    
    async def generate_climate_table_image(
        self,
        scenario_code: str,
        variable_code: str,
        start_year: int,
        end_year: int,
        current_user: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """기후 시나리오 데이터를 테이블 이미지로 생성"""
        try:
            # 데이터베이스에서 기후 데이터 조회
            climate_data = await self.repository.get_climate_scenarios(
                scenario_code=scenario_code,
                variable_code=variable_code,
                start_year=start_year,
                end_year=end_year
            )
            
            if not climate_data:
                raise Exception("해당 조건의 기후 데이터를 찾을 수 없습니다")
            
            # 테이블 이미지 생성
            image_data = await self._create_climate_table_image(
                climate_data, scenario_code, variable_code, start_year, end_year
            )
            
            return {
                "success": True,
                "image_data": image_data,
                "message": "기후 시나리오 테이블 이미지 생성 완료"
            }
            
        except Exception as e:
            logger.error(f"기후 시나리오 테이블 이미지 생성 실패: {str(e)}")
            raise Exception(f"기후 시나리오 테이블 이미지 생성 실패: {str(e)}")
    
    async def _create_climate_table_image(
        self,
        climate_data: List[Dict[str, Any]],
        scenario_code: str,
        variable_code: str,
        start_year: int,
        end_year: int
    ) -> str:
        """기후 데이터를 테이블 이미지로 변환"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.font_manager as fm
            import io
            import base64
            
            # 한글 폰트 설정
            plt.rcParams['font.family'] = 'DejaVu Sans'
            
            # 데이터를 연도별로 정리
            years = []
            values = []
            
            for data in climate_data:
                if 'year' in data and 'value' in data:
                    years.append(data['year'])
                    values.append(data['value'])
            
            if not years or not values:
                raise Exception("유효한 기후 데이터가 없습니다")
            
            # 테이블 데이터 생성
            table_data = []
            for i, year in enumerate(years):
                if start_year <= year <= end_year:
                    table_data.append([year, f"{values[i]:.2f}"])
            
            if not table_data:
                raise Exception("지정된 연도 범위에 데이터가 없습니다")
            
            # 테이블 이미지 생성
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.axis('tight')
            ax.axis('off')
            
            # 테이블 생성
            table = ax.table(
                cellText=table_data,
                colLabels=['연도', '값'],
                cellLoc='center',
                loc='center'
            )
            
            # 테이블 스타일링
            table.auto_set_font_size(False)
            table.set_fontsize(12)
            table.scale(1.2, 1.5)
            
            # 제목 설정
            scenario_names = {"SSP126": "SSP1-2.6 (저탄소)", "SSP585": "SSP5-8.5 (고탄소)"}
            variable_names = {
                "HW33": "폭염일수", "RN": "연강수량", "TA": "연평균기온", 
                "TR25": "열대야일수", "RAIN80": "호우일수"
            }
            
            title = f"{scenario_names.get(scenario_code, scenario_code)} - {variable_names.get(variable_code, variable_code)}\n({start_year}년 ~ {end_year}년)"
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            
            # 이미지를 base64로 인코딩
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"테이블 이미지 생성 실패: {str(e)}")
            raise Exception(f"테이블 이미지 생성 실패: {str(e)}")
    
    async def get_tcfd_inputs(self, db) -> List[Dict[str, Any]]:
        """TCFD 입력 데이터 조회 (가장 최신 데이터 포함)"""
        try:
            logger.info("🔍 TCFD 입력 데이터 조회 시작")
            
            # tcfd_inputs 테이블에서 데이터 조회
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                # Railway 환경: 비동기 처리
                from app.common.models import TCFDInput
                result = await db.execute(select(TCFDInput).order_by(TCFDInput.created_at.desc()))
                inputs = result.scalars().all()
            else:
                # Docker 환경: 동기 처리
                from sqlalchemy.orm import Session
                if isinstance(db, Session):
                    from app.common.models import TCFDInput
                    result = db.execute(select(TCFDInput).order_by(TCFDInput.created_at.desc()))
                    inputs = result.scalars().all()
                else:
                    # 비동기 세션인 경우
                    from app.common.models import TCFDInput
                    result = await db.execute(select(TCFDInput).order_by(TCFDInput.created_at.desc()))
                    inputs = result.scalars().all()
            
            # SQLAlchemy 객체를 딕셔너리로 변환
            inputs_list = []
            for input_data in inputs:
                input_dict = {
                    "id": input_data.id,
                    "governance_g1": input_data.governance_g1,
                    "governance_g2": input_data.governance_g2,
                    "strategy_s1": input_data.strategy_s1,
                    "strategy_s2": input_data.strategy_s2,
                    "strategy_s3": input_data.strategy_s3,
                    "risk_management_r1": input_data.risk_management_r1,
                    "risk_management_r2": input_data.risk_management_r2,
                    "risk_management_r3": input_data.risk_management_r3,
                    "metrics_targets_m1": input_data.metrics_targets_m1,
                    "metrics_targets_m2": input_data.metrics_targets_m2,
                    "metrics_targets_m3": input_data.metrics_targets_m3,
                    "created_at": input_data.created_at.isoformat() if input_data.created_at else None,
                    "updated_at": input_data.updated_at.isoformat() if input_data.updated_at else None
                }
                inputs_list.append(input_dict)
            
            logger.info(f"✅ TCFD 입력 데이터 조회 성공: {len(inputs_list)}개 레코드")
            return inputs_list
            
        except Exception as e:
            logger.error(f"❌ TCFD 입력 데이터 조회 실패: {str(e)}")
            logger.error(f"❌ 오류 타입: {type(e).__name__}")
            import traceback
            logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
            raise Exception(f"TCFD 입력 데이터 조회 실패: {str(e)}")

    async def close(self):
        """리소스 정리"""
        await self.repository.close()
