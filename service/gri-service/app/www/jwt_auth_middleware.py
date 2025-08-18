from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.domain.auth.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)
security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=401,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="토큰에 사용자 정보가 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"user_id": int(user_id)}
        
    except Exception as e:
        logger.error(f"토큰 검증 실패: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="토큰 검증에 실패했습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
