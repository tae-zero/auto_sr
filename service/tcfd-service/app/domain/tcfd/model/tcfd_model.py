"""
TCFD Service TCFD Pydantic 모델
- API 요청/응답 데이터 검증
- 데이터 전송 객체 (DTO)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

class CompanyInfoRequest(BaseModel):
    """회사 정보 요청 모델"""
    company_name: str = Field(..., description="회사명")
    industry: str = Field(..., description="업종")
    size: str = Field(..., description="기업 규모")
    location: str = Field(..., description="위치")
    established_year: Optional[int] = Field(None, description="설립년도")
    
    @validator('company_name')
    def validate_company_name(cls, v):
        if not v or not v.strip():
            raise ValueError('회사명을 입력해주세요')
        return v.strip()
    
    @validator('industry')
    def validate_industry(cls, v):
        if not v or not v.strip():
            raise ValueError('업종을 입력해주세요')
        return v.strip()

class FinancialDataRequest(BaseModel):
    """재무 데이터 요청 모델"""
    table_name: str = Field(..., description="테이블명")
    data: Dict[str, Any] = Field(..., description="재무 데이터")
    
    @validator('table_name')
    def validate_table_name(cls, v):
        valid_tables = ['employee', 'profit', 'executive', 'financial', 'corporation']
        if v not in valid_tables:
            raise ValueError(f'지원하지 않는 테이블입니다. 지원 테이블: {", ".join(valid_tables)}')
        return v
    
    @validator('data')
    def validate_data(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError('데이터는 딕셔너리 형태여야 합니다')
        return v

class RiskAssessmentRequest(BaseModel):
    """위험 평가 요청 모델"""
    assessment_type: str = Field(..., description="평가 유형")
    risk_factors: List[Dict[str, Any]] = Field(..., description="위험 요소들")
    climate_scenarios: Optional[List[str]] = Field(None, description="기후 시나리오")
    
    @validator('assessment_type')
    def validate_assessment_type(cls, v):
        valid_types = ['physical', 'transitional', 'comprehensive']
        if v not in valid_types:
            raise ValueError(f'지원하지 않는 평가 유형입니다. 지원 유형: {", ".join(valid_types)}')
        return v

class TCFDAnalysisResponse(BaseModel):
    """TCFD 분석 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    data: Optional[Dict[str, Any]] = Field(None, description="분석 결과 데이터")
    message: str = Field(..., description="응답 메시지")
    analysis_id: Optional[str] = Field(None, description="분석 ID")
    timestamp: Optional[datetime] = Field(None, description="응답 시간")

class RiskAssessmentResponse(BaseModel):
    """위험 평가 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    data: Optional[Dict[str, Any]] = Field(None, description="위험 평가 결과")
    message: str = Field(..., description="응답 메시지")
    risk_score: Optional[float] = Field(None, description="위험 점수")
    assessment_id: Optional[str] = Field(None, description="평가 ID")
    timestamp: Optional[datetime] = Field(None, description="응답 시간")

class ReportGenerationResponse(BaseModel):
    """보고서 생성 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    data: Optional[Dict[str, Any]] = Field(None, description="보고서 데이터")
    message: str = Field(..., description="응답 메시지")
    report_id: Optional[str] = Field(None, description="보고서 ID")
    report_url: Optional[str] = Field(None, description="보고서 다운로드 URL")
    timestamp: Optional[datetime] = Field(None, description="응답 시간")

class FinancialDataResponse(BaseModel):
    """재무 데이터 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    data: Dict[str, List[Dict[str, Any]]] = Field(..., description="재무 데이터")
    total_records: int = Field(..., description="총 레코드 수")
    tables: List[str] = Field(..., description="테이블 목록")
    message: str = Field(..., description="응답 메시지")

class ClimateScenarioRequest(BaseModel):
    """기후 시나리오 요청 모델"""
    scenario_type: str = Field(..., description="시나리오 유형")
    time_horizon: int = Field(..., description="시간 범위 (년)")
    temperature_rise: float = Field(..., description="온도 상승 (도)")
    
    @validator('time_horizon')
    def validate_time_horizon(cls, v):
        if v < 1 or v > 100:
            raise ValueError('시간 범위는 1-100년 사이여야 합니다')
        return v
    
    @validator('temperature_rise')
    def validate_temperature_rise(cls, v):
        if v < 0 or v > 10:
            raise ValueError('온도 상승은 0-10도 사이여야 합니다')
        return v
