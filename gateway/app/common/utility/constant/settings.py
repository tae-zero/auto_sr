from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Gateway 설정
    GATEWAY_HOST: str = "0.0.0.0"
    GATEWAY_PORT: int = 8080
    GATEWAY_RELOAD: bool = True
    
    # 환경변수 설정
    DEPLOYMENT_ENV: str = "development"
    RAILWAY_ENVIRONMENT: bool = False
    USE_RAILWAY_TCFD: bool = False
    USE_LOCAL_AUTH: bool = True
    USE_LOCAL_CHATBOT: bool = True
    
    # JWT 설정
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN_DAYS: int = 30
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    
    # 요청 설정
    REQUEST_TIMEOUT: int = 30
    HEALTH_CHECK_INTERVAL: int = 30
    
    # CORS 설정
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://frontend:3000"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 추가 환경변수 무시 