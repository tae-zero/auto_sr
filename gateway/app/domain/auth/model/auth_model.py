"""
Gateway Auth Pydantic 모델
- API 요청/응답 데이터 검증
- 데이터 전송 객체 (DTO)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

class AuthRequest(BaseModel):
    """인증 요청 모델"""
    company_id: Optional[str] = Field(None, description="회사 ID")
    industry: Optional[str] = Field(None, description="업종")
    email: str = Field(..., description="이메일")
    name: Optional[str] = Field(None, description="이름")
    age: Optional[str] = Field(None, description="나이")
    auth_id: str = Field(..., description="아이디")
    auth_pw: str = Field(..., description="비밀번호")
    
    @validator('email')
    def validate_email(cls, v):
        if not v or '@' not in v:
            raise ValueError('유효한 이메일 주소를 입력해주세요')
        return v
    
    @validator('auth_pw')
    def validate_password(cls, v):
        if not v or len(v) < 6:
            raise ValueError('비밀번호는 6자 이상이어야 합니다')
        return v

class AuthResponse(BaseModel):
    """인증 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    data: Optional[Dict[str, Any]] = Field(None, description="응답 데이터")
    message: str = Field(..., description="응답 메시지")
    error: Optional[str] = Field(None, description="에러 메시지")
    timestamp: Optional[datetime] = Field(None, description="응답 시간")

class UserInfo(BaseModel):
    """사용자 정보 모델"""
    user_id: str = Field(..., description="사용자 ID")
    email: str = Field(..., description="이메일")
    name: Optional[str] = Field(None, description="이름")
    company_id: Optional[str] = Field(None, description="회사 ID")
    industry: Optional[str] = Field(None, description="업종")
    status: str = Field(..., description="계정 상태")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")

class LoginRequest(BaseModel):
    """로그인 요청 모델"""
    auth_id: str = Field(..., description="아이디")
    auth_pw: str = Field(..., description="비밀번호")
    
    @validator('auth_id')
    def validate_auth_id(cls, v):
        if not v or not v.strip():
            raise ValueError('아이디를 입력해주세요')
        return v.strip()
    
    @validator('auth_pw')
    def validate_auth_pw(cls, v):
        if not v or not v.strip():
            raise ValueError('비밀번호를 입력해주세요')
        return v.strip()

class LoginResponse(BaseModel):
    """로그인 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    user_info: Optional[UserInfo] = Field(None, description="사용자 정보")
    token: Optional[str] = Field(None, description="JWT 토큰")
    refresh_token: Optional[str] = Field(None, description="리프레시 토큰")
    message: str = Field(..., description="응답 메시지")
    timestamp: datetime = Field(..., description="응답 시간")

class TokenValidation(BaseModel):
    """토큰 검증 모델"""
    token: str = Field(..., description="검증할 토큰")
    
    @validator('token')
    def validate_token(cls, v):
        if not v or not v.strip():
            raise ValueError('토큰이 필요합니다')
        return v.strip()

class TokenRefresh(BaseModel):
    """토큰 갱신 모델"""
    refresh_token: str = Field(..., description="리프레시 토큰")
    
    @validator('refresh_token')
    def validate_refresh_token(cls, v):
        if not v or not v.strip():
            raise ValueError('리프레시 토큰이 필요합니다')
        return v.strip()
