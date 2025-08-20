"""
Gateway Auth Pydantic 모델
- API 요청/응답 데이터 검증
- 데이터 전송 객체 (DTO)
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from datetime import datetime

class AuthRequest(BaseModel):
    """인증 요청 모델 (회원가입용)"""
    email: str = Field(..., description="이메일")
    auth_id: str = Field(..., description="아이디")
    auth_pw: str = Field(..., description="비밀번호")
    name: Optional[str] = Field(default="", description="이름")
    age: Optional[str] = Field(default="", description="나이")
    company_id: Optional[str] = Field(default="", description="회사 ID")
    industry: Optional[str] = Field(default="", description="업종")

class AuthResponse(BaseModel):
    """인증 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    token: Optional[str] = Field(None, description="JWT 토큰")
    user_id: Optional[Union[str, int]] = Field(None, description="사용자 ID")  # 문자열 또는 정수 허용
    email: Optional[str] = Field(None, description="이메일")
    name: Optional[str] = Field(None, description="사용자 이름")
    company_id: Optional[str] = Field(None, description="회사 ID")
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

class TokenRefresh(BaseModel):
    """토큰 갱신 모델"""
    refresh_token: str = Field(..., description="리프레시 토큰")
