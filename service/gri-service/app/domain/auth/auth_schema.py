from pydantic import BaseModel, EmailStr
from typing import Optional

class UserSignupRequest(BaseModel):
    email: str
    auth_id: str
    auth_pw: str
    name: str
    age: str
    company_id: str
    industry: str

class UserLoginRequest(BaseModel):
    auth_id: str
    auth_pw: str

class UserResponse(BaseModel):
    id: int
    email: str
    auth_id: str
    name: str
    age: str
    company_id: str
    industry: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[TokenResponse] = None
