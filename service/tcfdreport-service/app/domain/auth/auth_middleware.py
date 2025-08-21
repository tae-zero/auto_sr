from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from typing import Optional, Dict
import os
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# JWT 시크릿 키 (환경변수에서 가져오거나 기본값 사용)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "esg-mate-super-secret-key-2025-railway-deployment-2025")
ALGORITHM = "HS256"

# JWT Secret 키 로깅 (디버깅용)
logger.info(f"🔐 TCFD Report Service JWT_SECRET_KEY 로드: {SECRET_KEY[:20]}...")

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """
    JWT 토큰을 검증하고 현재 사용자 정보를 반환합니다.
    """
    try:
        logger.info(f"🔍 JWT 토큰 검증 시작: {credentials.credentials[:20]}...")
        logger.info(f"🔐 사용 중인 SECRET_KEY: {SECRET_KEY[:20]}...")
        logger.info(f"🔐 SECRET_KEY 전체 길이: {len(SECRET_KEY)}")
        logger.info(f"🔐 ALGORITHM: {ALGORITHM}")
        
        # 토큰 헤더 확인 (디버깅용)
        try:
            token_header = jwt.get_unverified_header(credentials.credentials)
            logger.info(f"🔍 토큰 헤더 정보: {token_header}")
        except Exception as e:
            logger.warning(f"⚠️ 토큰 헤더 확인 실패: {str(e)}")
        
        # 토큰 디코딩
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"✅ JWT 토큰 디코딩 성공: {payload}")
        
        user_id: str = payload.get("user_id")  # sub 대신 user_id 사용
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            logger.error(f"❌ 토큰에 필수 정보 누락: user_id={user_id}, email={email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_info = {
            "user_id": user_id,
            "email": email,
            "name": payload.get("name", "N/A"),
            "company_id": payload.get("company_id", "N/A")  # company_id 추가
        }
        
        logger.info(f"✅ 사용자 정보 추출 성공: {user_info}")
        return user_info
        
    except ExpiredSignatureError:
        logger.error("❌ JWT 토큰 만료")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        logger.error(f"❌ JWT 토큰 검증 실패: {str(e)}")
        logger.error(f"❌ 토큰 내용: {credentials.credentials}")
        logger.error(f"❌ SECRET_KEY: {SECRET_KEY}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰을 검증할 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"❌ JWT 토큰 처리 중 예상치 못한 오류: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 처리 중 오류가 발생했습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
