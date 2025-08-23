from pydantic_settings import BaseSettings
from typing import List, Dict, Optional
import os

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/database_name")
    
    # Gateway 설정
    GATEWAY_HOST: str = os.getenv("GATEWAY_HOST", "0.0.0.0")
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8080"))
    GATEWAY_RELOAD: bool = os.getenv("GATEWAY_RELOAD", "false").lower() == "true"
    
    # Railway 환경 설정
    RAILWAY_ENVIRONMENT: bool = os.getenv("RAILWAY_ENVIRONMENT", "false").lower() == "true"
    USE_LOCAL_AUTH: bool = os.getenv("USE_LOCAL_AUTH", "true").lower() == "true"
    USE_LOCAL_CHATBOT: bool = os.getenv("USE_LOCAL_CHATBOT", "true").lower() == "true"
    USE_RAILWAY_TCFD: bool = os.getenv("USE_RAILWAY_TCFD", "false").lower() == "true"
    
    # Railway Service URLs (프로덕션 환경)
    RAILWAY_AUTH_SERVICE_URL: str = os.getenv("RAILWAY_AUTH_SERVICE_URL", "")
    RAILWAY_CHATBOT_SERVICE_URL: str = os.getenv("RAILWAY_CHATBOT_SERVICE_URL", "")
    RAILWAY_TCFD_SERVICE_URL: str = os.getenv("RAILWAY_TCFD_SERVICE_URL", "")
    RAILWAY_TCFD_REPORT_SERVICE_URL: str = os.getenv("RAILWAY_TCFD_REPORT_SERVICE_URL", "")
    
    # Service Ports (로컬 개발 환경)
    AUTH_SERVICE_PORT: int = int(os.getenv("AUTH_SERVICE_PORT", "8008"))
    CHATBOT_SERVICE_PORT: int = int(os.getenv("CHATBOT_SERVICE_PORT", "8001"))
    TCFD_SERVICE_PORT: int = int(os.getenv("TCFD_SERVICE_PORT", "8005"))
    
    # AI 및 LangChain 설정
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # 벡터 데이터베이스 설정
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "chroma")  # chroma, faiss
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # 문서 처리 설정
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    SUPPORTED_FILE_TYPES: List[str] = os.getenv("SUPPORTED_FILE_TYPES", "txt,pdf,docx,md").split(",")
    
    # 서비스 디스커버리 설정
    SERVICE_DISCOVERY_TYPE: str = os.getenv("SERVICE_DISCOVERY_TYPE", "static")  # static, consul, eureka
    CONSUL_HOST: str = os.getenv("CONSUL_HOST", "localhost")
    CONSUL_PORT: int = int(os.getenv("CONSUL_PORT", "8500"))
    
    # 로드 밸런서 설정
    LOAD_BALANCER_TYPE: str = os.getenv("LOAD_BALANCER_TYPE", "round_robin")  # round_robin, least_connections, random
    
    # 타임아웃 설정
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "30"))
    
    # 로깅 설정
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS 설정
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", '["*"]').replace("'", '"').replace('"', '"').split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: List[str] = os.getenv("CORS_ALLOW_METHODS", '["*"]').replace("'", '"').replace('"', '"').split(",")
    CORS_ALLOW_HEADERS: List[str] = os.getenv("CORS_ALLOW_HEADERS", '["*"]').replace("'", '"').replace('"', '"').split(",")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 전역 설정 인스턴스
settings = Settings()

# 서비스 레지스트리 설정 (Railway 환경 감지)
# ... existing code ...

# 서비스 레지스트리 설정 (Railway 환경 감지)
def get_service_registry():
    """Railway 환경인지 확인하고 적절한 서비스 레지스트리 반환"""
    railway_env = os.getenv("RAILWAY_ENVIRONMENT", "false").lower() == "true"
    if railway_env:  # boolean 값으로 직접 확인
        # Railway 프로덕션 환경
        return {
            "auth-service": {
                "instances": [
                    {"host": settings.RAILWAY_AUTH_SERVICE_URL.replace("https://", "").split("/")[0], "port": 443, "health": True, "weight": 1, "ssl": True},
                ],
                "load_balancer": "round_robin",
                "current_index": 0,
                "health_check_path": "/health"
            },
            "chatbot-service": {
                "instances": [
                    {"host": settings.RAILWAY_CHATBOT_SERVICE_URL.replace("https://", "").split("/")[0], "port": 443, "health": True, "weight": 1, "ssl": True},
                ],
                "load_balancer": "round_robin",
                "current_index": 0,
                "health_check_path": "/health"
            },
            "tcfd-service": {
                "instances": [
                    {"host": settings.RAILWAY_TCFD_SERVICE_URL.replace("https://", "").split("/")[0], "port": 443, "health": True, "weight": 1, "ssl": True},
                ],
                "load_balancer": "round_robin",
                "current_index": 0,
                "health_check_path": "/health"
            },
            "tcfd-report-service": {
                "instances": [
                    {"host": settings.RAILWAY_TCFD_REPORT_SERVICE_URL.replace("https://", "").split("/")[0], "port": 443, "health": True, "weight": 1, "ssl": True},
                ],
                "load_balancer": "round_robin",
                "current_index": 0,
                "health_check_path": "/health"
            }
        }
    else:
        # 로컬 개발 환경
        return {
            "auth-service": {
                "instances": [
                    {"host": "localhost", "port": settings.AUTH_SERVICE_PORT, "health": True, "weight": 1},
                ],
                "load_balancer": "round_robin",
                "current_index": 0,
                "health_check_path": "/health"
            },
            "chatbot-service": {
                "instances": [
                    {"host": "localhost", "port": settings.CHATBOT_SERVICE_PORT, "health": True, "weight": 1},
                ],
                "load_balancer": "round_robin",
                "current_index": 0,
                "health_check_path": "/health"
            },
            "tcfd-service": {
                "instances": [
                    {"host": "localhost", "port": settings.TCFD_SERVICE_PORT, "health": True, "weight": 1},
                ],
                "load_balancer": "round_robin",
                "current_index": 0,
                "health_check_path": "/health"
            },
            "tcfdreport-service": {
                "instances": [
                    {"host": "tcfdreport-service", "port": 8004, "health": True, "weight": 1},
                ],
                "load_balancer": "round_robin",
                "current_index": 0,
                "health_check_path": "/health"
            }
        }

# ... existing code ...

# 동적 서비스 레지스트리
DEFAULT_SERVICE_REGISTRY = get_service_registry() 