from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os

def parse_bool(value: str) -> bool:
    """다양한 형태의 문자열을 boolean으로 파싱"""
    print(f"🔍 parse_bool 호출됨: value='{value}', type={type(value)}")  # 디버깅 로그
    
    if isinstance(value, bool):
        print(f"✅ 이미 boolean: {value}")
        return value
    
    if not isinstance(value, str):
        print(f"❌ 문자열이 아님: {value}")
        return False
    
    # 따옴표 제거 및 공백 제거
    original_value = value
    value = value.strip().strip('"').strip("'")
    print(f"🔧 문자열 정리: '{original_value}' -> '{value}'")
    
    # 다양한 true/false 표현 처리
    true_values = ['true', '1', 'yes', 'on', 'production']
    false_values = ['false', '0', 'no', 'off', 'development']
    
    if value.lower() in true_values:
        print(f"✅ true로 인식: '{value}'")
        return True
    elif value.lower() in false_values:
        print(f"✅ false로 인식: '{value}'")
        return False
    
    print(f"❌ 알 수 없는 값: '{value}', 기본값 false 반환")
    return False

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
    
    # Railway Service URLs (프로덕션 환경)
    RAILWAY_AUTH_SERVICE_URL: str = os.getenv("RAILWAY_AUTH_SERVICE_URL", "")
    RAILWAY_CHATBOT_SERVICE_URL: str = os.getenv("RAILWAY_CHATBOT_SERVICE_URL", "")
    RAILWAY_TCFD_SERVICE_URL: str = os.getenv("RAILWAY_TCFD_SERVICE_URL", "")
    RAILWAY_TCFD_REPORT_SERVICE_URL: str = os.getenv("RAILWAY_TCFD_REPORT_SERVICE_URL", "")
    RAILWAY_GRI_SERVICE_URL: str = os.getenv("RAILWAY_GRI_SERVICE_URL", "")
    RAILWAY_MATERIALITY_SERVICE_URL: str = os.getenv("RAILWAY_MATERIALITY_SERVICE_URL", "")
    
    # Service Ports (로컬 개발 환경)
    AUTH_SERVICE_PORT: int = int(os.getenv("AUTH_SERVICE_PORT", "8008"))
    CHATBOT_SERVICE_PORT: int = int(os.getenv("CHATBOT_SERVICE_PORT", "8001"))
    TCFD_SERVICE_PORT: int = int(os.getenv("TCFD_SERVICE_PORT", "8005"))
    
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
    
    # Pydantic validators
    @field_validator('RAILWAY_ENVIRONMENT', mode='before')
    @classmethod
    def validate_railway_environment(cls, v):
        if isinstance(v, str):
            return parse_bool(v)
        return v
    
    @field_validator('USE_LOCAL_AUTH', mode='before')
    @classmethod
    def validate_use_local_auth(cls, v):
        if isinstance(v, str):
            return parse_bool(v)
        return v
    
    @field_validator('USE_LOCAL_CHATBOT', mode='before')
    @classmethod
    def validate_use_local_chatbot(cls, v):
        if isinstance(v, str):
            return parse_bool(v)
        return v
    
    @field_validator('USE_RAILWAY_TCFD', mode='before')
    @classmethod
    def validate_use_railway_tcfd(cls, v):
        if isinstance(v, str):
            return parse_bool(v)
        return v
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 추가 환경변수 무시 