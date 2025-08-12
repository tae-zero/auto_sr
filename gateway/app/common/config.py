from pydantic_settings import BaseSettings
from typing import List, Dict, Optional
import os

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://postgres:YgIQJWEaQShbuQhRsAdVaeBUZatEgrQO@postgres.railway.internal:5432/railway"
    
    # Gateway 설정
    GATEWAY_HOST: str = "0.0.0.0"
    GATEWAY_PORT: int = int(os.getenv("GATEWAY_PORT", "8080"))
    GATEWAY_RELOAD: bool = True
    
    # Railway Service URLs (프로덕션 환경)
    RAILWAY_AUTH_SERVICE_URL: str = os.getenv("RAILWAY_AUTH_SERVICE_URL", "")
    RAILWAY_CHATBOT_SERVICE_URL: str = os.getenv("RAILWAY_CHATBOT_SERVICE_URL", "")
    
    # Service Ports (로컬 개발 환경)
    AUTH_SERVICE_PORT: int = int(os.getenv("AUTH_SERVICE_PORT", "8008"))
    CHATBOT_SERVICE_PORT: int = int(os.getenv("CHATBOT_SERVICE_PORT", "8006"))
    
    # 서비스 디스커버리 설정
    SERVICE_DISCOVERY_TYPE: str = "static"  # static, consul, eureka
    CONSUL_HOST: str = "localhost"
    CONSUL_PORT: int = 8500
    
    # 로드 밸런서 설정
    LOAD_BALANCER_TYPE: str = "round_robin"  # round_robin, least_connections, random
    
    # 타임아웃 설정
    REQUEST_TIMEOUT: int = 30
    HEALTH_CHECK_INTERVAL: int = 30
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    
    # CORS 설정
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# 전역 설정 인스턴스
settings = Settings()

# 서비스 레지스트리 설정 (Railway 환경 감지)
def get_service_registry():
    """Railway 환경인지 확인하고 적절한 서비스 레지스트리 반환"""
    if settings.RAILWAY_AUTH_SERVICE_URL:
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
            }
        }

# 동적 서비스 레지스트리
DEFAULT_SERVICE_REGISTRY = get_service_registry() 