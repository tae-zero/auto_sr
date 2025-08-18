from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TCFDInputCreateSchema(BaseModel):
    """TCFD 입력 데이터 생성 스키마"""
    
    company_name: str = Field(..., description="회사명", min_length=1, max_length=255)
    user_id: Optional[str] = Field(None, description="사용자 ID", max_length=255)
    
    # TCFD 11개 인덱스 텍스트 필드
    governance_g1: Optional[str] = Field(None, description="G1: 기후 관련 위험과 기회에 대한 이사회 감독")
    governance_g2: Optional[str] = Field(None, description="G2: 기후 관련 위험과 기회에 대한 경영진 역할")
    
    strategy_s1: Optional[str] = Field(None, description="S1: 기후 관련 위험과 기회의 비즈니스 영향")
    strategy_s2: Optional[str] = Field(None, description="S2: 전략적 영향의 실제 잠재적 영향")
    strategy_s3: Optional[str] = Field(None, description="S3: 기후 시나리오 분석")
    
    risk_management_r1: Optional[str] = Field(None, description="R1: 기후 관련 위험 식별 및 평가 프로세스")
    risk_management_r2: Optional[str] = Field(None, description="R2: 위험 관리 프로세스 통합")
    risk_management_r3: Optional[str] = Field(None, description="R3: 위험 관리 프로세스")
    
    metrics_targets_m1: Optional[str] = Field(None, description="M1: 기후 관련 위험 평가 지표")
    metrics_targets_m2: Optional[str] = Field(None, description="M2: 기후 관련 기회 평가 지표")
    metrics_targets_m3: Optional[str] = Field(None, description="M3: 기후 관련 목표 설정")

class TCFDInputUpdateSchema(BaseModel):
    """TCFD 입력 데이터 업데이트 스키마"""
    
    governance_g1: Optional[str] = Field(None, description="G1: 기후 관련 위험과 기회에 대한 이사회 감독")
    governance_g2: Optional[str] = Field(None, description="G2: 기후 관련 위험과 기회에 대한 경영진 역할")
    
    strategy_s1: Optional[str] = Field(None, description="S1: 기후 관련 위험과 기회의 비즈니스 영향")
    strategy_s2: Optional[str] = Field(None, description="S2: 전략적 영향의 실제 잠재적 영향")
    strategy_s3: Optional[str] = Field(None, description="S3: 기후 시나리오 분석")
    
    risk_management_r1: Optional[str] = Field(None, description="R1: 기후 관련 위험 식별 및 평가 프로세스")
    risk_management_r2: Optional[str] = Field(None, description="R2: 위험 관리 프로세스 통합")
    risk_management_r3: Optional[str] = Field(None, description="R3: 위험 관리 프로세스")
    
    metrics_targets_m1: Optional[str] = Field(None, description="M1: 기후 관련 위험 평가 지표")
    metrics_targets_m2: Optional[str] = Field(None, description="M2: 기후 관련 기회 평가 지표")
    metrics_targets_m3: Optional[str] = Field(None, description="M3: 기후 관련 목표 설정")

class TCFDInputResponseSchema(BaseModel):
    """TCFD 입력 데이터 응답 스키마"""
    
    id: int = Field(..., description="입력 데이터 ID")
    company_name: str = Field(..., description="회사명")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    
    # TCFD 11개 인덱스 텍스트 필드
    governance_g1: Optional[str] = Field(None, description="G1: 기후 관련 위험과 기회에 대한 이사회 감독")
    governance_g2: Optional[str] = Field(None, description="G2: 기후 관련 위험과 기회에 대한 경영진 역할")
    
    strategy_s1: Optional[str] = Field(None, description="S1: 기후 관련 위험과 기회의 비즈니스 영향")
    strategy_s2: Optional[str] = Field(None, description="S2: 전략적 영향의 실제 잠재적 영향")
    strategy_s3: Optional[str] = Field(None, description="S3: 기후 시나리오 분석")
    
    risk_management_r1: Optional[str] = Field(None, description="R1: 기후 관련 위험 식별 및 평가 프로세스")
    risk_management_r2: Optional[str] = Field(None, description="R2: 위험 관리 프로세스 통합")
    risk_management_r3: Optional[str] = Field(None, description="R3: 위험 관리 프로세스")
    
    metrics_targets_m1: Optional[str] = Field(None, description="M1: 기후 관련 위험 평가 지표")
    metrics_targets_m2: Optional[str] = Field(None, description="M2: 기후 관련 기회 평가 지표")
    metrics_targets_m3: Optional[str] = Field(None, description="M3: 기후 관련 목표 설정")
    
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")
    
    class Config:
        from_attributes = True
