from pydantic_settings import BaseSettings
from typing import List, Dict, Optional
import os

class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # Gateway 설정
    GATEWAY_HOST: str = "0.0.0.0"
    GATEWAY_PORT: int = 8080
    GATEWAY_RELOAD: bool = True
    
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

# 서비스 레지스트리 설정 (Gateway만 배포)
DEFAULT_SERVICE_REGISTRY = {
    "user-service": {
        "instances": [
            {"host": "localhost", "port": 8001, "health": True, "weight": 1},
            {"host": "localhost", "port": 8002, "health": True, "weight": 1}
        ],
        "load_balancer": "round_robin",
        "current_index": 0,
        "health_check_path": "/health"
    },
    "order-service": {
        "instances": [
            {"host": "localhost", "port": 8003, "health": True, "weight": 1},
            {"host": "localhost", "port": 8004, "health": True, "weight": 1}
        ],
        "load_balancer": "round_robin",
        "current_index": 0,
        "health_check_path": "/health"
    },
    "product-service": {
        "instances": [
            {"host": "localhost", "port": 8005, "health": True, "weight": 1}
        ],
        "load_balancer": "round_robin",
        "current_index": 0,
        "health_check_path": "/health"
    }
} 