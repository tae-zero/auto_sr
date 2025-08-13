"""
Gateway Auth 스키마
- 인증 데이터 스키마 및 응답 모델
- 토큰 검증 및 사용자 정보
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class AuthValidation(BaseModel):
    """인증 검증 결과"""
    valid: bool = Field(..., description="검증 성공 여부")
    user_info: Optional[Dict[str, Any]] = Field(None, description="사용자 정보")
    message: str = Field(..., description="검증 메시지")
    expires_at: Optional[datetime] = Field(None, description="토큰 만료 시간")

class AuthStatus(BaseModel):
    """인증 상태 정보"""
    user_id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="이메일")
    status: str = Field(..., description="계정 상태")
    last_login: Optional[datetime] = Field(None, description="마지막 로그인")
    failed_attempts: int = Field(0, description="실패한 로그인 시도 횟수")
    is_locked: bool = Field(False, description="계정 잠금 여부")

class LoginAttempt(BaseModel):
    """로그인 시도 정보"""
    email: str = Field(..., description="이메일")
    timestamp: datetime = Field(..., description="시도 시간")
    success: bool = Field(..., description="성공 여부")
    ip_address: Optional[str] = Field(None, description="IP 주소")
    user_agent: Optional[str] = Field(None, description="사용자 에이전트")
    failure_reason: Optional[str] = Field(None, description="실패 사유")

class SecurityMetrics(BaseModel):
    """보안 지표"""
    total_logins: int = Field(0, description="총 로그인 시도")
    successful_logins: int = Field(0, description="성공한 로그인")
    failed_logins: int = Field(0, description="실패한 로그인")
    success_rate: float = Field(0.0, description="성공률")
    average_response_time: float = Field(0.0, description="평균 응답 시간 (ms)")
    last_security_incident: Optional[datetime] = Field(None, description="마지막 보안 사고")

class AuthAuditLog(BaseModel):
    """인증 감사 로그"""
    log_id: str = Field(..., description="로그 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    action: str = Field(..., description="수행된 작업")
    timestamp: datetime = Field(..., description="작업 시간")
    ip_address: Optional[str] = Field(None, description="IP 주소")
    user_agent: Optional[str] = Field(None, description="사용자 에이전트")
    details: Optional[Dict[str, Any]] = Field(None, description="상세 정보")
    status: str = Field(..., description="작업 상태")

class PasswordPolicy(BaseModel):
    """비밀번호 정책"""
    min_length: int = Field(8, description="최소 길이")
    require_uppercase: bool = Field(True, description="대문자 포함 필수")
    require_lowercase: bool = Field(True, description="소문자 포함 필수")
    require_numbers: bool = Field(True, description="숫자 포함 필수")
    require_special_chars: bool = Field(True, description="특수문자 포함 필수")
    max_age_days: int = Field(90, description="최대 사용 기간 (일)")
    prevent_reuse_count: int = Field(5, description="재사용 방지 개수")

class AccountLockoutPolicy(BaseModel):
    """계정 잠금 정책"""
    max_failed_attempts: int = Field(5, description="최대 실패 시도 횟수")
    lockout_duration_minutes: int = Field(30, description="잠금 지속 시간 (분)")
    lockout_threshold_minutes: int = Field(15, description="잠금 임계값 시간 (분)")
    progressive_delay: bool = Field(True, description="점진적 지연 적용")
    admin_notification: bool = Field(True, description="관리자 알림")
