from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from app.domain.auth.auth_middleware import get_current_user
from app.domain.tcfd.controller.tcfd_controller import TCFDController

router = APIRouter(prefix="/api/v1/tcfd", tags=["tcfd"])

@router.get("/company-overview")
async def get_company_overview(
    company_name: str = Query(..., description="회사명"),
    user_id: Optional[str] = Query(None, description="사용자 ID"),
    email: Optional[str] = Query(None, description="사용자 이메일"),
    company_id: Optional[str] = Query(None, description="회사 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    회사별 기업개요 정보 조회
    """
    try:
        controller = TCFDController()
        result = await controller.get_company_overview(
            company_name=company_name,
            user_id=user_id,
            email=email,
            company_id=company_id,
            current_user=current_user
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"회사 정보 조회 실패: {str(e)}")

@router.get("/standards")
async def get_tcfd_standards(
    user_id: Optional[str] = Query(None, description="사용자 ID"),
    email: Optional[str] = Query(None, description="사용자 이메일"),
    name: Optional[str] = Query(None, description="사용자 이름"),
    company_id: Optional[str] = Query(None, description="회사 ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    TCFD 표준 정보 조회
    """
    try:
        controller = TCFDController()
        result = await controller.get_tcfd_standards(
            user_id=user_id,
            email=email,
            name=name,
            company_id=company_id,
            current_user=current_user
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TCFD 표준 정보 조회 실패: {str(e)}")
