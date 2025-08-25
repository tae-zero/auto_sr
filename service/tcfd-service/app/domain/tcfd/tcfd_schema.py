"""
TCFD Service TCFD 스키마
- TCFD 데이터 스키마 및 응답 모델
- AI 분석 결과, 위험 평가, 보고서 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# TCFD 표준 정보 스키마
class TCFDStandardResponse(BaseModel):
    """TCFD 표준 정보 응답 스키마"""
    # id 필드 제거 (실제 DB에 없음)
    category: str = Field(..., description="카테고리")
    disclosure_id: str = Field(..., description="공개 ID")
    disclosure_summary: str = Field(..., description="공개 요약")
    disclosure_detail: str = Field(..., description="공개 상세")

    class Config:
        from_attributes = True

class TCFDStandardsListResponse(BaseModel):
    """TCFD 표준 정보 목록 응답 스키마"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    data: List[TCFDStandardResponse] = Field(..., description="TCFD 표준 정보 목록")

class TCFDReport(BaseModel):
    """TCFD 보고서 스키마"""
    report_id: str = Field(..., description="보고서 ID")
    company_name: str = Field(..., description="회사명")
    report_date: datetime = Field(..., description="보고서 작성일")
    governance: Dict[str, Any] = Field(..., description="거버넌스")
    strategy: Dict[str, Any] = Field(..., description="전략")
    risk_management: Dict[str, Any] = Field(..., description="위험 관리")
    metrics_targets: Dict[str, Any] = Field(..., description="지표 및 목표")
    status: str = Field(..., description="상태")

class ClimateRisk(BaseModel):
    """기후 위험 스키마"""
    risk_id: str = Field(..., description="위험 ID")
    risk_type: str = Field(..., description="위험 유형")
    risk_level: str = Field(..., description="위험 수준")
    probability: float = Field(..., description="발생 확률")
    impact: str = Field(..., description="영향도")
    mitigation_strategies: List[str] = Field(..., description="완화 전략")
    assessment_date: datetime = Field(..., description="평가일")

class FinancialMetrics(BaseModel):
    """재무 지표 스키마"""
    metric_id: str = Field(..., description="지표 ID")
    metric_name: str = Field(..., description="지표명")
    current_value: float = Field(..., description="현재값")
    target_value: Optional[float] = Field(None, description="목표값")
    unit: str = Field(..., description="단위")
    trend: str = Field(..., description="추세")
    last_updated: datetime = Field(..., description="최종 업데이트")

class ClimateScenario(BaseModel):
    """기후 시나리오 스키마"""
    scenario_id: str = Field(..., description="시나리오 ID")
    scenario_name: str = Field(..., description="시나리오명")
    temperature_rise: float = Field(..., description="온도 상승 (도)")
    time_horizon: int = Field(..., description="시간 범위 (년)")
    probability: float = Field(..., description="발생 확률")
    description: str = Field(..., description="설명")
    financial_impact: Dict[str, Any] = Field(..., description="재무적 영향")

class TCFDAnalysisResult(BaseModel):
    """TCFD 분석 결과 스키마"""
    analysis_id: str = Field(..., description="분석 ID")
    document_type: str = Field(..., description="문서 유형")
    analysis_summary: str = Field(..., description="분석 요약")
    key_findings: List[str] = Field(..., description="주요 발견사항")
    recommendations: List[str] = Field(..., description="권장사항")
    confidence_score: float = Field(..., description="신뢰도 점수")
    analysis_date: datetime = Field(..., description="분석일")

class RiskAssessmentResult(BaseModel):
    """위험 평가 결과 스키마"""
    assessment_id: str = Field(..., description="평가 ID")
    overall_risk_score: float = Field(..., description="전체 위험 점수")
    physical_risks: List[ClimateRisk] = Field(..., description="물리적 위험")
    transition_risks: List[ClimateRisk] = Field(..., description="전환 위험")
    risk_categories: Dict[str, float] = Field(..., description="위험 카테고리별 점수")
    assessment_date: datetime = Field(..., description="평가일")

class ReportTemplate(BaseModel):
    """보고서 템플릿 스키마"""
    template_id: str = Field(..., description="템플릿 ID")
    template_name: str = Field(..., description="템플릿명")
    industry: str = Field(..., description="업종")
    sections: List[str] = Field(..., description="섹션 목록")
    required_fields: List[str] = Field(..., description="필수 필드")
    version: str = Field(..., description="버전")
    last_updated: datetime = Field(..., description="최종 업데이트")

class ComplianceCheck(BaseModel):
    """준수성 검사 스키마"""
    check_id: str = Field(..., description="검사 ID")
    company_name: str = Field(..., description="회사명")
    compliance_score: float = Field(..., description="준수성 점수")
    check_date: datetime = Field(..., description="검사일")
    issues: List[str] = Field(..., description="발견된 문제점")
    recommendations: List[str] = Field(..., description="개선 권장사항")

# 기업개요 정보 스키마 추가
class CompanyOverview(BaseModel):
    """기업개요 정보 스키마"""
    종목코드: str = Field(..., description="주식 종목 코드")
    종목명: str = Field(..., description="회사명")
    주소: Optional[str] = Field(None, description="회사 주소")
    설립일: Optional[str] = Field(None, description="회사 설립일")
    대표자: Optional[str] = Field(None, description="대표자명")
    전화번호: Optional[str] = Field(None, description="연락처")
    홈페이지: Optional[str] = Field(None, description="회사 웹사이트")

class CompanyOverviewResponse(BaseModel):
    """기업개요 정보 응답 스키마"""
    success: bool = Field(..., description="성공 여부")
    company_name: str = Field(..., description="검색한 회사명")
    overview: CompanyOverview = Field(..., description="기업개요 정보")

class StakeholderEngagement(BaseModel):
    """이해관계자 참여 스키마"""
    engagement_id: str = Field(..., description="참여 ID")
    stakeholder_type: str = Field(..., description="이해관계자 유형")
    engagement_method: str = Field(..., description="참여 방법")
    topics_discussed: List[str] = Field(..., description="논의 주제")
    feedback: str = Field(..., description="피드백")
    action_items: List[str] = Field(..., description="행동 항목")
    engagement_date: datetime = Field(..., description="참여일")

class PerformanceMetrics(BaseModel):
    """성과 지표 스키마"""
    metric_id: str = Field(..., description="지표 ID")
    metric_category: str = Field(..., description="지표 카테고리")
    metric_name: str = Field(..., description="지표명")
    baseline_value: float = Field(..., description="기준값")
    current_value: float = Field(..., description="현재값")
    target_value: float = Field(..., description="목표값")
    achievement_rate: float = Field(..., description="달성률")
    measurement_date: datetime = Field(..., description="측정일")
