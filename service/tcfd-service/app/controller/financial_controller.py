"""
재무정보 컨트롤러
- 재무정보 CRUD API 엔드포인트
- 요청/응답 처리 및 검증
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel

from app.model.financial_model import FinancialDataCreate, FinancialDataUpdate, FinancialDataResponse
from app.service.financial_service import FinancialService
from app.schema.financial_schema import FinancialDataListResponse

router = APIRouter(prefix="/api/v1/financial-data", tags=["재무정보"])

@router.get("/", response_model=FinancialDataListResponse)
async def get_financial_data(
    company_id: Optional[str] = Query(None, description="회사 ID"),
    fiscal_year: Optional[str] = Query(None, description="회계연도")
):
    """재무정보 조회"""
    try:
        service = FinancialService()
        data = await service.get_financial_data(company_id, fiscal_year)
        return FinancialDataListResponse(
            success=True,
            data=data,
            message="재무정보 조회 성공"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{financial_id}", response_model=FinancialDataResponse)
async def get_financial_data_by_id(financial_id: str):
    """ID로 재무정보 조회"""
    try:
        service = FinancialService()
        data = await service.get_financial_data_by_id(financial_id)
        if not data:
            raise HTTPException(status_code=404, detail="재무정보를 찾을 수 없습니다")
        return FinancialDataResponse(
            success=True,
            data=data,
            message="재무정보 조회 성공"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=FinancialDataResponse)
async def create_financial_data(data: FinancialDataCreate):
    """재무정보 생성"""
    try:
        service = FinancialService()
        created_data = await service.create_financial_data(data)
        return FinancialDataResponse(
            success=True,
            data=created_data,
            message="재무정보 생성 성공"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{financial_id}", response_model=FinancialDataResponse)
async def update_financial_data(financial_id: str, data: FinancialDataUpdate):
    """재무정보 업데이트"""
    try:
        service = FinancialService()
        updated_data = await service.update_financial_data(financial_id, data)
        if not updated_data:
            raise HTTPException(status_code=404, detail="재무정보를 찾을 수 없습니다")
        return FinancialDataResponse(
            success=True,
            data=updated_data,
            message="재무정보 업데이트 성공"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{financial_id}")
async def delete_financial_data(financial_id: str):
    """재무정보 삭제"""
    try:
        service = FinancialService()
        success = await service.delete_financial_data(financial_id)
        if not success:
            raise HTTPException(status_code=404, detail="재무정보를 찾을 수 없습니다")
        return {"success": True, "message": "재무정보 삭제 성공"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/ratios/{financial_id}")
async def get_financial_ratios(financial_id: str):
    """재무지표 분석"""
    try:
        service = FinancialService()
        ratios = await service.calculate_financial_ratios(financial_id)
        return {
            "success": True,
            "data": ratios,
            "message": "재무지표 분석 완료"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
