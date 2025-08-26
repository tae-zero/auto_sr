from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TCFDInput(BaseModel):
    """TCFD 권고사항 입력 데이터 모델 (실제 테이블 구조 기반)"""
    id: Optional[int] = None
    company_name: Optional[str] = None
    user_id: Optional[str] = None
    
    # Governance 관련
    governance_g1: Optional[str] = None
    governance_g2: Optional[str] = None
    
    # Strategy 관련
    strategy_s1: Optional[str] = None
    strategy_s2: Optional[str] = None
    strategy_s3: Optional[str] = None
    
    # Risk Management 관련
    risk_management_r1: Optional[str] = None
    risk_management_r2: Optional[str] = None
    risk_management_r3: Optional[str] = None
    
    # Metrics and Targets 관련
    metrics_targets_m1: Optional[str] = None
    metrics_targets_m2: Optional[str] = None
    metrics_targets_m3: Optional[str] = None
    
    # 기타 필드들 (테이블에 더 있을 수 있음)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TCFDReportRequest(BaseModel):
    """TCFD 보고서 생성 요청 모델"""
    company_name: str
    report_year: str
    tcfd_inputs: TCFDInput
    report_type: str = "draft"  # draft, polished
    llm_provider: str = "openai"  # openai, huggingface

class TCFDReportResponse(BaseModel):
    """TCFD 보고서 생성 응답 모델"""
    success: bool
    report_content: Optional[str] = None
    error_message: Optional[str] = None
    generated_at: datetime
    llm_provider: str
    report_type: str
