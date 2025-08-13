"""
재무정보 Pydantic 모델
- API 요청/응답 데이터 검증
- 데이터 전송 객체 (DTO)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class FinancialDataBase(BaseModel):
    """재무정보 기본 모델"""
    company_id: str = Field(..., description="회사 ID")
    fiscal_year: str = Field(..., description="회계연도")
    revenue: float = Field(..., gt=0, description="매출액 (백만원)")
    total_assets: float = Field(..., gt=0, description="자산총액 (백만원)")
    total_liabilities: float = Field(..., ge=0, description="부채총액 (백만원)")
    total_equity: float = Field(..., gt=0, description="자본총액 (백만원)")
    operating_income: Optional[float] = Field(None, description="영업이익 (백만원)")
    net_income: Optional[float] = Field(None, description="당기순이익 (백만원)")
    
    @validator('total_assets')
    def validate_accounting_equation(cls, v, values):
        """재무제표 기본 등식 검증 (자산 = 부채 + 자본)"""
        if 'total_liabilities' in values and 'total_equity' in values:
            calculated_assets = values['total_liabilities'] + values['total_equity']
            difference = abs(v - calculated_assets)
            if difference > 0.01:  # 0.01 백만원 이상 차이나면 경고
                raise ValueError(f"자산총액({v})이 부채총액({values['total_liabilities']})과 자본총액({values['total_equity']})의 합({calculated_assets})과 일치하지 않습니다")
        return v

class FinancialDataCreate(FinancialDataBase):
    """재무정보 생성 모델"""
    pass

class FinancialDataUpdate(BaseModel):
    """재무정보 업데이트 모델"""
    company_id: Optional[str] = Field(None, description="회사 ID")
    fiscal_year: Optional[str] = Field(None, description="회계연도")
    revenue: Optional[float] = Field(None, gt=0, description="매출액 (백만원)")
    total_assets: Optional[float] = Field(None, gt=0, description="자산총액 (백만원)")
    total_liabilities: Optional[float] = Field(None, ge=0, description="부채총액 (백만원)")
    total_equity: Optional[float] = Field(None, gt=0, description="자본총액 (백만원)")
    operating_income: Optional[float] = Field(None, description="영업이익 (백만원)")
    net_income: Optional[float] = Field(None, description="당기순이익 (백만원)")

class FinancialData(FinancialDataBase):
    """재무정보 응답 모델"""
    id: str = Field(..., description="재무정보 ID")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FinancialDataResponse(BaseModel):
    """재무정보 응답 래퍼 모델"""
    success: bool = Field(..., description="성공 여부")
    data: Optional[FinancialData] = Field(None, description="재무정보 데이터")
    message: str = Field(..., description="응답 메시지")
    error: Optional[str] = Field(None, description="에러 메시지")

class FinancialDataListResponse(BaseModel):
    """재무정보 목록 응답 래퍼 모델"""
    success: bool = Field(..., description="성공 여부")
    data: list[FinancialData] = Field(..., description="재무정보 목록")
    message: str = Field(..., description="응답 메시지")
    error: Optional[str] = Field(None, description="에러 메시지")
