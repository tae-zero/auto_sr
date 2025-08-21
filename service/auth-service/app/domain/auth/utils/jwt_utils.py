"""JWT 관련 유틸리티 함수"""
import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# 로깅 설정
logger = logging.getLogger(__name__)

def create_token(user_data: Dict[str, Any], expires_in_days: int = 30) -> str:
    """JWT 토큰 생성
    
    Args:
        user_data (Dict[str, Any]): 사용자 데이터
        expires_in_days (int, optional): 토큰 만료 기간(일). Defaults to 30.
    
    Returns:
        str: JWT 토큰
    """
    # JWT 시크릿 키
    secret_key = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-here")
    
    # JWT Secret 키 로깅 (디버깅용)
    logger.info(f"🔐 Auth Service JWT_SECRET_KEY 로드: {secret_key[:20]}...")
    logger.info(f"🔐 Auth Service JWT_SECRET_KEY 전체 길이: {len(secret_key)}")
    
    # 토큰 페이로드
    payload = {
        "user_id": str(user_data.get("user_id")),
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "company_id": user_data.get("company_id"),
        "exp": datetime.utcnow() + timedelta(days=expires_in_days)
    }
    
    # 토큰 생성
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    logger.info(f"✅ JWT 토큰 생성 완료: {token[:20]}...")
    return token

def verify_token(token: str) -> Dict[str, Any]:
    """JWT 토큰 검증
    
    Args:
        token (str): JWT 토큰
    
    Returns:
        Dict[str, Any]: 검증 결과
    """
    try:
        # JWT 시크릿 키
        secret_key = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-here")
        
        # 토큰 디코드 및 검증
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # 만료 시간 확인
        exp = datetime.fromtimestamp(payload.get("exp"))
        if exp < datetime.utcnow():
            return {
                "valid": False,
                "message": "토큰이 만료되었습니다"
            }
        
        return {
            "valid": True,
            "user_info": {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "name": payload.get("name"),
                "company_id": payload.get("company_id")
            },
            "message": "토큰이 유효합니다"
        }
        
    except jwt.ExpiredSignatureError:
        return {
            "valid": False,
            "message": "토큰이 만료되었습니다"
        }
    except jwt.InvalidTokenError:
        return {
            "valid": False,
            "message": "유효하지 않은 토큰입니다"
        }
