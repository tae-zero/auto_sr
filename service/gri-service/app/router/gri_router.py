from fastapi import APIRouter, Depends, HTTPException
from app.www.jwt_auth_middleware import get_current_user
from app.domain.auth import auth_controller

router = APIRouter()

# 인증 관련 라우터
router.include_router(auth_controller.router, prefix="/auth", tags=["인증"])

@router.get("/reports")
async def get_gri_reports(current_user: dict = Depends(get_current_user)):
    """GRI 보고서 목록 조회 (인증 필요)"""
    return {
        "success": True,
        "message": "GRI 보고서 목록",
        "data": []
    }

@router.post("/reports")
async def create_gri_report(current_user: dict = Depends(get_current_user)):
    """GRI 보고서 생성 (인증 필요)"""
    return {
        "success": True,
        "message": "GRI 보고서가 생성되었습니다.",
        "data": {"user_id": current_user["user_id"]}
    }

@router.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {"status": "healthy", "service": "gri-report-service"}
