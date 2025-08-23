"""
MSA 서비스 공통 설정 및 유틸리티
"""
import os
import logging
from typing import Optional, Dict, Any
from functools import wraps
import time

# 공통 로깅 설정
def setup_logging(service_name: str, log_level: str = "INFO") -> logging.Logger:
    """서비스별 로깅 설정"""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 이미 핸들러가 설정되어 있지 않은 경우에만 추가
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# 공통 환경변수 설정
def get_service_config(service_name: str) -> Dict[str, Any]:
    """서비스별 환경변수 설정 가져오기"""
    return {
        "SERVICE_NAME": os.getenv("SERVICE_NAME", service_name),
        "SERVICE_HOST": os.getenv("SERVICE_HOST", "0.0.0.0"),
        "SERVICE_PORT": int(os.getenv("SERVICE_PORT", os.getenv("PORT", "8000"))),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
        "RAILWAY_ENVIRONMENT": os.getenv("RAILWAY_ENVIRONMENT", "false").lower() == "true",
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-here"),
    }

# 공통 예외 처리 데코레이터
def handle_service_errors(func):
    """서비스 함수의 예외를 처리하는 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(func.__module__)
            logger.error(f"서비스 함수 오류 ({func.__name__}): {e}")
            raise
    return wrapper

# 공통 헬스체크 응답
def create_health_response(
    service_name: str, 
    status: str = "healthy", 
    additional_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """표준화된 헬스체크 응답 생성"""
    response = {
        "status": status,
        "service": service_name,
        "timestamp": time.time(),
        "architecture": "MSV Pattern with Layered Architecture"
    }
    
    if additional_info:
        response.update(additional_info)
    
    return response

# 공통 CORS 설정
def get_cors_origins() -> list:
    """공통 CORS origin 설정"""
    return [
        "http://localhost:3000",  # 로컬 프론트엔드
        "http://localhost:3001",  # 로컬 프론트엔드 (포트 3001)
        "http://127.0.0.1:3000",  # 로컬 IP
        "http://127.0.0.1:3001",  # 로컬 IP (포트 3001)
        "http://frontend:3000",   # Docker 내부 네트워크
        "https://www.taezero.com",  # 프로덕션 도메인
        "https://taezero.com",      # 프로덕션 도메인 (www 없이)
        "https://*.up.railway.app",  # Railway 모든 서브도메인
        "https://*.railway.app",     # Railway 모든 도메인
        "*"  # 개발 환경에서 모든 origin 허용
    ]

# 공통 에러 메시지
class ServiceErrorMessages:
    """서비스별 공통 에러 메시지"""
    
    DATABASE_CONNECTION_FAILED = "데이터베이스 연결 실패"
    SERVICE_UNAVAILABLE = "서비스 일시적 사용 불가"
    INVALID_REQUEST = "잘못된 요청"
    UNAUTHORIZED = "인증 필요"
    FORBIDDEN = "권한 없음"
    NOT_FOUND = "리소스를 찾을 수 없음"
    INTERNAL_ERROR = "내부 서버 오류"
    
    @classmethod
    def get_message(cls, error_type: str, service_name: str = "") -> str:
        """에러 메시지 가져오기"""
        base_message = getattr(cls, error_type.upper(), cls.INTERNAL_ERROR)
        if service_name:
            return f"{service_name}: {base_message}"
        return base_message

# 공통 성능 모니터링
def monitor_performance(func):
    """함수 실행 시간을 모니터링하는 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger = logging.getLogger(func.__module__)
            logger.info(f"{func.__name__} 실행 시간: {execution_time:.3f}초")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger = logging.getLogger(func.__module__)
            logger.error(f"{func.__name__} 실행 실패 (시간: {execution_time:.3f}초): {e}")
            raise
    return wrapper
