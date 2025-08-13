"""
재무정보 스키마
- 재무지표 계산 결과
- TCFD 분석 결과
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class FinancialRatios(BaseModel):
    """재무지표 계산 결과"""
    debt_ratio: float = Field(..., description="부채비율 (부채총액/자본총액)")
    equity_ratio: float = Field(..., description="자기자본비율 (자본총액/자산총액)")
    operating_margin: Optional[float] = Field(None, description="영업이익률 (영업이익/매출액)")
    net_margin: Optional[float] = Field(None, description="순이익률 (당기순이익/매출액)")
    roa: Optional[float] = Field(None, description="ROA (당기순이익/자산총액)")
    roe: Optional[float] = Field(None, description="ROE (당기순이익/자본총액)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "debt_ratio": 1.5,
                "equity_ratio": 0.4,
                "operating_margin": 0.08,
                "net_margin": 0.05,
                "roa": 0.06,
                "roe": 0.15
            }
        }

class FinancialAnalysis(BaseModel):
    """재무분석 결과"""
    financial_id: str = Field(..., description="재무정보 ID")
    ratios: FinancialRatios = Field(..., description="재무지표")
    risk_assessment: str = Field(..., description="위험도 평가")
    recommendations: List[str] = Field(..., description="개선 권장사항")
    
    class Config:
        json_schema_extra = {
            "example": {
                "financial_id": "uuid-string",
                "ratios": {
                    "debt_ratio": 1.5,
                    "equity_ratio": 0.4,
                    "operating_margin": 0.08,
                    "net_margin": 0.05,
                    "roa": 0.06,
                    "roe": 0.15
                },
                "risk_assessment": "보통",
                "recommendations": [
                    "부채비율을 낮추기 위한 자본조달 검토",
                    "수익성 개선을 위한 비용 구조 최적화"
                ]
            }
        }

class TCFDRiskAssessment(BaseModel):
    """TCFD 위험 평가 결과"""
    financial_id: str = Field(..., description="재무정보 ID")
    climate_risk_score: float = Field(..., ge=0, le=100, description="기후 위험 점수 (0-100)")
    transition_risk_score: float = Field(..., ge=0, le=100, description="전환 위험 점수 (0-100)")
    physical_risk_score: float = Field(..., ge=0, le=100, description="물리적 위험 점수 (0-100)")
    overall_risk_level: str = Field(..., description="전체 위험 수준")
    risk_factors: List[str] = Field(..., description="주요 위험 요소")
    mitigation_strategies: List[str] = Field(..., description="위험 완화 전략")
    
    class Config:
        json_schema_extra = {
            "example": {
                "financial_id": "uuid-string",
                "climate_risk_score": 65.5,
                "transition_risk_score": 72.0,
                "physical_risk_score": 58.0,
                "overall_risk_level": "중간",
                "risk_factors": [
                    "에너지 의존도가 높음",
                    "탄소 배출량이 업계 평균 이상"
                ],
                "mitigation_strategies": [
                    "재생에너지 전환 가속화",
                    "탄소 중립 목표 설정 및 실행"
                ]
            }
        }

class FinancialDataSummary(BaseModel):
    """재무정보 요약"""
    total_companies: int = Field(..., description="총 회사 수")
    total_financial_records: int = Field(..., description="총 재무기록 수")
    average_revenue: float = Field(..., description="평균 매출액")
    average_assets: float = Field(..., description="평균 자산총액")
    risk_distribution: dict = Field(..., description="위험 수준별 분포")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_companies": 150,
                "total_financial_records": 450,
                "average_revenue": 25000.0,
                "average_assets": 50000.0,
                "risk_distribution": {
                    "낮음": 30,
                    "보통": 45,
                    "높음": 25
                }
            }
        }
