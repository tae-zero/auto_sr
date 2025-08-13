"""
재무정보 서비스
- 재무정보 비즈니스 로직 처리
- 재무지표 계산 및 분석
"""
from typing import List, Optional, Dict, Any
from app.repository.financial_repository import FinancialRepository
from app.model.financial_model import FinancialDataCreate, FinancialDataUpdate, FinancialData
from app.schema.financial_schema import FinancialRatios

class FinancialService:
    def __init__(self):
        self.repository = FinancialRepository()
    
    async def get_financial_data(self, company_id: Optional[str] = None, fiscal_year: Optional[str] = None) -> List[FinancialData]:
        """재무정보 조회"""
        try:
            return await self.repository.get_financial_data(company_id, fiscal_year)
        except Exception as e:
            raise Exception(f"재무정보 조회 실패: {str(e)}")
    
    async def get_financial_data_by_id(self, financial_id: str) -> Optional[FinancialData]:
        """ID로 재무정보 조회"""
        try:
            return await self.repository.get_financial_data_by_id(financial_id)
        except Exception as e:
            raise Exception(f"재무정보 조회 실패: {str(e)}")
    
    async def create_financial_data(self, data: FinancialDataCreate) -> FinancialData:
        """재무정보 생성"""
        try:
            # 비즈니스 로직 검증
            self._validate_financial_data(data)
            
            # 재무제표 기본 등식 검증
            self._validate_accounting_equation(data)
            
            return await self.repository.create_financial_data(data)
        except Exception as e:
            raise Exception(f"재무정보 생성 실패: {str(e)}")
    
    async def update_financial_data(self, financial_id: str, data: FinancialDataUpdate) -> Optional[FinancialData]:
        """재무정보 업데이트"""
        try:
            # 기존 데이터 조회
            existing_data = await self.repository.get_financial_data_by_id(financial_id)
            if not existing_data:
                raise Exception("재무정보를 찾을 수 없습니다")
            
            # 업데이트 데이터 검증
            self._validate_financial_data_update(data)
            
            return await self.repository.update_financial_data(financial_id, data)
        except Exception as e:
            raise Exception(f"재무정보 업데이트 실패: {str(e)}")
    
    async def delete_financial_data(self, financial_id: str) -> bool:
        """재무정보 삭제"""
        try:
            return await self.repository.delete_financial_data(financial_id)
        except Exception as e:
            raise Exception(f"재무정보 삭제 실패: {str(e)}")
    
    async def calculate_financial_ratios(self, financial_id: str) -> FinancialRatios:
        """재무지표 계산"""
        try:
            financial_data = await self.repository.get_financial_data_by_id(financial_id)
            if not financial_data:
                raise Exception("재무정보를 찾을 수 없습니다")
            
            return self._calculate_ratios(financial_data)
        except Exception as e:
            raise Exception(f"재무지표 계산 실패: {str(e)}")
    
    def _validate_financial_data(self, data: FinancialDataCreate) -> None:
        """재무정보 검증"""
        if not data.revenue or data.revenue <= 0:
            raise ValueError("매출액은 0보다 큰 값이어야 합니다")
        
        if not data.total_assets or data.total_assets <= 0:
            raise ValueError("자산총액은 0보다 큰 값이어야 합니다")
        
        if not data.total_liabilities or data.total_liabilities < 0:
            raise ValueError("부채총액은 0 이상이어야 합니다")
        
        if not data.total_equity or data.total_equity <= 0:
            raise ValueError("자본총액은 0보다 큰 값이어야 합니다")
        
        if not data.fiscal_year:
            raise ValueError("회계연도를 입력해주세요")
        
        if not data.company_id:
            raise ValueError("회사 ID가 필요합니다")
    
    def _validate_financial_data_update(self, data: FinancialDataUpdate) -> None:
        """재무정보 업데이트 검증"""
        if hasattr(data, 'revenue') and data.revenue is not None and data.revenue <= 0:
            raise ValueError("매출액은 0보다 큰 값이어야 합니다")
        
        if hasattr(data, 'total_assets') and data.total_assets is not None and data.total_assets <= 0:
            raise ValueError("자산총액은 0보다 큰 값이어야 합니다")
    
    def _validate_accounting_equation(self, data: FinancialDataCreate) -> None:
        """재무제표 기본 등식 검증 (자산 = 부채 + 자본)"""
        calculated_assets = data.total_liabilities + data.total_equity
        difference = abs(data.total_assets - calculated_assets)
        
        if difference > 0.01:  # 0.01 백만원 이상 차이나면 경고
            raise ValueError(f"자산총액({data.total_assets})이 부채총액({data.total_liabilities})과 자본총액({data.total_equity})의 합({calculated_assets})과 일치하지 않습니다")
    
    def _calculate_ratios(self, data: FinancialData) -> FinancialRatios:
        """재무지표 계산"""
        return FinancialRatios(
            debt_ratio=data.total_liabilities / data.total_equity,
            equity_ratio=data.total_equity / data.total_assets,
            operating_margin=data.operating_income / data.revenue if data.operating_income else None,
            net_margin=data.net_income / data.revenue if data.net_income else None,
            roa=data.net_income / data.total_assets if data.net_income else None,
            roe=data.net_income / data.total_equity if data.net_income else None
        )
