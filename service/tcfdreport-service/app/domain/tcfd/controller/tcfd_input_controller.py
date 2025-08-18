"""
TCFD 입력 데이터 컨트롤러
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
import logging
from app.domain.tcfd.schema.tcfd_input_schema import (
    TCFDInputCreateSchema,
    TCFDInputResponseSchema
)
from app.domain.tcfd.service.tcfd_input_service import TCFDInputService
from app.common.database.database import database

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tcfdreport", tags=["tcfd-input"])

async def get_tcfd_service():
    """TCFD 서비스 의존성 주입"""
    return TCFDInputService()

@router.post("/inputs", response_model=TCFDInputResponseSchema)
async def create_tcfd_input(
    data: TCFDInputCreateSchema,
    service: TCFDInputService = Depends(get_tcfd_service)
):
    """TCFD 입력 데이터 생성"""
    try:
        result = await service.create_input(data)
        return result
    except Exception as e:
        logger.error(f"TCFD 입력 데이터 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inputs", response_model=List[TCFDInputResponseSchema])
async def get_tcfd_inputs(
    company_name: Optional[str] = None,
    user_id: Optional[str] = None,
    service: TCFDInputService = Depends(get_tcfd_service)
):
    """TCFD 입력 데이터 조회"""
    try:
        if company_name:
            result = await service.get_inputs_by_company(company_name)
        elif user_id:
            result = await service.get_inputs_by_user(user_id)
        else:
            result = await service.get_all_inputs()
        return result
    except Exception as e:
        logger.error(f"TCFD 입력 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/inputs/{input_id}", response_model=TCFDInputResponseSchema)
async def get_tcfd_input(
    input_id: int,
    service: TCFDInputService = Depends(get_tcfd_service)
):
    """특정 TCFD 입력 데이터 조회"""
    try:
        result = await service.get_input_by_id(input_id)
        if not result:
            raise HTTPException(status_code=404, detail="TCFD 입력 데이터를 찾을 수 없습니다")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TCFD 입력 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
