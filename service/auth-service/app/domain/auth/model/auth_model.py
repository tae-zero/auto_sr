"""
Auth Service Auth Pydantic 모델
- API 요청/응답 데이터 검증
- 데이터 전송 객체 (DTO)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Union
from datetime import datetime

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

class SignupRequest(BaseModel):
    """회원가입 요청 모델"""
    company_id: str = Field(..., description="회사 ID")
    industry: str = Field(..., description="업종")
    email: str = Field(..., description="이메일")
    name: str = Field(..., description="이름")
    age: str = Field(..., description="나이")
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
    
    @validator('auth_id')
    def validate_auth_id(cls, v):
        if not v or not v.strip():
            raise ValueError('아이디를 입력해주세요')
        return v.strip()

class AuthResponse(BaseModel):
    """인증 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    user_id: Optional[Union[str, int]] = Field(None, description="사용자 ID")  # 문자열 또는 정수 허용
    email: Optional[str] = Field(None, description="이메일")
    name: Optional[str] = Field(None, description="사용자 이름")
    company_id: Optional[str] = Field(None, description="회사 ID")
    token: Optional[str] = Field(None, description="JWT 토큰")
    error: Optional[str] = Field(None, description="에러 메시지")
    timestamp: Optional[datetime] = Field(None, description="응답 시간")

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
