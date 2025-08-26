from fastapi import HTTPException, Header, status
from typing import Optional
from ..common.config import ADMIN_TOKEN
import logging

logger = logging.getLogger(__name__)

async def verify_admin_token(x_admin_token: Optional[str] = Header(None)) -> bool:
    """
    관리자 토큰을 검증합니다.
    
    Args:
        x_admin_token: X-ADMIN-TOKEN 헤더 값
        
    Returns:
        bool: 토큰이 유효하면 True
        
    Raises:
        HTTPException: 토큰이 유효하지 않으면 401 에러
    """
    if not x_admin_token:
        logger.warning("관리자 토큰이 제공되지 않음")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="관리자 토큰이 필요합니다. X-ADMIN-TOKEN 헤더를 포함해주세요."
        )
    
    if x_admin_token != ADMIN_TOKEN:
        logger.warning(f"잘못된 관리자 토큰 시도: {x_admin_token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 관리자 토큰입니다."
        )
    
    logger.info("관리자 토큰 검증 성공")
    return True

def get_admin_token() -> str:
    """
    현재 설정된 관리자 토큰을 반환합니다.
    
    Returns:
        str: 관리자 토큰
    """
    return ADMIN_TOKEN
