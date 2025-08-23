from fastapi import APIRouter, HTTPException, Depends
from app.www.jwt_auth_middleware import get_current_user

router = APIRouter()

@router.get("/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """토큰 검증 및 사용자 정보 반환"""
    return {
        "success": True,
        "message": "토큰이 유효합니다.",
        "data": current_user
    }