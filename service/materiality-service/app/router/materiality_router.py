from fastapi import APIRouter, Depends, HTTPException
from app.www.jwt_auth_middleware import get_current_user
from app.domain.auth import auth_controller
from app.domain.controller import materiality_controller

router = APIRouter()

# 인증 관련 라우터
router.include_router(auth_controller.router, prefix="/auth", tags=["인증"])

# Materiality 데이터 관련 라우터
router.include_router(materiality_controller.router, prefix="/data", tags=["Materiality 데이터"])

@router.get("/analyses")
async def get_materiality_analyses(current_user: dict = Depends(get_current_user)):
    """Materiality 분석 목록 조회 (인증 필요)"""
    return {
        "success": True,
        "message": "Materiality 분석 목록",
        "data": []
    }

@router.post("/analyses")
async def create_materiality_analysis(current_user: dict = Depends(get_current_user)):
    """Materiality 분석 생성 (인증 필요)"""
    return {
        "success": True,
        "message": "Materiality 분석이 생성되었습니다.",
        "data": {"user_id": current_user["user_id"]}
    }

@router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy", "service": "materiality-service"}
