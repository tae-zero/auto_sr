from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from app.common.database.database import get_db
from app.common.models import User
from app.domain.auth.auth_schema import UserSignupRequest, UserLoginRequest, UserResponse, TokenResponse

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    def __init__(self):
        self.pwd_context = pwd_context
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    async def signup(self, user_data: UserSignupRequest) -> dict:
        db = next(get_db())
        
        # 기존 사용자 확인
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.auth_id == user_data.auth_id)
        ).first()
        
        if existing_user:
            return {"success": False, "message": "이미 존재하는 사용자입니다."}
        
        # 새 사용자 생성
        hashed_password = self.get_password_hash(user_data.auth_pw)
        new_user = User(
            email=user_data.email,
            auth_id=user_data.auth_id,
            auth_pw=hashed_password,
            name=user_data.name,
            age=user_data.age,
            company_id=user_data.company_id,
            industry=user_data.industry
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"success": True, "message": "회원가입이 완료되었습니다."}
    
    async def login(self, login_data: UserLoginRequest) -> dict:
        db = next(get_db())
        
        # 사용자 확인
        user = db.query(User).filter(User.auth_id == login_data.auth_id).first()
        if not user or not self.verify_password(login_data.auth_pw, user.auth_pw):
            return {"success": False, "message": "아이디 또는 비밀번호가 잘못되었습니다."}
        
        # JWT 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        
        # 사용자 정보 반환
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            auth_id=user.auth_id,
            name=user.name,
            age=user.age,
            company_id=user.company_id,
            industry=user.industry
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
        return {
            "success": True,
            "message": "로그인이 완료되었습니다.",
            "data": token_response
        }
