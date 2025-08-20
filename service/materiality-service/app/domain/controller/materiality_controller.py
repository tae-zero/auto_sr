from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.common.database.database import get_db
from app.domain.materiality_service import MaterialityService
from app.www.jwt_auth_middleware import get_current_user
from typing import List, Dict, Any, Optional

router = APIRouter()

# 프론트엔드용 데이터 엔드포인트 (인증 없이 접근 가능)
@router.get("/data/categories", tags=["프론트엔드용"])
async def get_categories_for_frontend(db: Session = Depends(get_db)):
    """프론트엔드용 카테고리 데이터 조회 (인증 불필요)"""
    try:
        service = MaterialityService(db)
        data = service.get_all_categories()
        return {
            "success": True,
            "message": "카테고리 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/kcgs", tags=["프론트엔드용"])
async def get_kcgs_for_frontend(db: Session = Depends(get_db)):
    """프론트엔드용 KCGS 데이터 조회 (인증 불필요)"""
    try:
        service = MaterialityService(db)
        data = service.get_all_kcgs()
        return {
            "success": True,
            "message": "KCGS 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/sasb", tags=["프론트엔드용"])
async def get_sasb_for_frontend(db: Session = Depends(get_db)):
    """프론트엔드용 SASB 데이터 조회 (인증 불필요)"""
    try:
        service = MaterialityService(db)
        data = service.get_all_sasb()
        return {
            "success": True,
            "message": "SASB 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/sustainbest-e", tags=["프론트엔드용"])
async def get_sustainbest_e_for_frontend(db: Session = Depends(get_db)):
    """프론트엔드용 서스틴베스트 E 데이터 조회 (인증 불필요)"""
    try:
        service = MaterialityService(db)
        data = service.get_all_sustainbest_e()
        return {
            "success": True,
            "message": "서스틴베스트 E 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/sustainbest-s", tags=["프론트엔드용"])
async def get_sustainbest_s_for_frontend(db: Session = Depends(get_db)):
    """프론트엔드용 서스틴베스트 S 데이터 조회 (인증 불필요)"""
    try:
        service = MaterialityService(db)
        data = service.get_all_sustainbest_s()
        return {
            "success": True,
            "message": "서스틴베스트 S 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/sustainbest-g", tags=["프론트엔드용"])
async def get_sustainbest_g_for_frontend(db: Session = Depends(get_db)):
    """프론트엔드용 서스틴베스트 G 데이터 조회 (인증 불필요)"""
    try:
        service = MaterialityService(db)
        data = service.get_all_sustainbest_g()
        return {
            "success": True,
            "message": "서스틴베스트 G 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Category Table Controllers
@router.get("/categories", tags=["카테고리"])
async def get_all_categories(db: Session = Depends(get_db)):
    """모든 카테고리 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_all_categories()
        return {
            "success": True,
            "message": "카테고리 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories/esg-division/{esg_division}", tags=["카테고리"])
async def get_categories_by_esg_division(
    esg_division: str,
    db: Session = Depends(get_db)
):
    """ESG 구분별 카테고리 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_categories_by_esg_division(esg_division)
        return {
            "success": True,
            "message": f"ESG 구분 '{esg_division}' 카테고리 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories/esg-divisions", tags=["카테고리"])
async def get_esg_divisions(db: Session = Depends(get_db)):
    """ESG 구분 목록 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_esg_divisions()
        return {
            "success": True,
            "message": "ESG 구분 목록 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# KCGS Table Controllers
@router.get("/kcgs", tags=["KCGS"])
async def get_all_kcgs(db: Session = Depends(get_db)):
    """모든 KCGS 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_all_kcgs()
        return {
            "success": True,
            "message": "KCGS 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kcgs/environment/{environment}", tags=["KCGS"])
async def get_kcgs_by_environment(
    environment: str,
    db: Session = Depends(get_db)
):
    """환경(E) 기준 KCGS 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_kcgs_by_environment(environment)
        return {
            "success": True,
            "message": f"환경 '{environment}' KCGS 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kcgs/social/{social}", tags=["KCGS"])
async def get_kcgs_by_social(
    social: str,
    db: Session = Depends(get_db)
):
    """사회(S) 기준 KCGS 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_kcgs_by_social(social)
        return {
            "success": True,
            "message": f"사회 '{social}' KCGS 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/kcgs/governance/{governance}", tags=["KCGS"])
async def get_kcgs_by_governance(
    governance: str,
    db: Session = Depends(get_db)
):
    """거버넌스(G) 기준 KCGS 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_kcgs_by_governance(governance)
        return {
            "success": True,
            "message": f"거버넌스 '{governance}' KCGS 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# SASB Table Controllers
@router.get("/sasb", tags=["SASB"])
async def get_all_sasb(db: Session = Depends(get_db)):
    """모든 SASB 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_all_sasb()
        return {
            "success": True,
            "message": "SASB 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sasb/industry/{industry}", tags=["SASB"])
async def get_sasb_by_industry(
    industry: str,
    db: Session = Depends(get_db)
):
    """산업별 SASB 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_sasb_by_industry(industry)
        return {
            "success": True,
            "message": f"산업 '{industry}' SASB 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sasb/industries", tags=["SASB"])
async def get_sasb_industries(db: Session = Depends(get_db)):
    """SASB 산업 목록 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_sasb_industries()
        return {
            "success": True,
            "message": "SASB 산업 목록 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sustainbest E Table Controllers
@router.get("/sustainbest-e", tags=["서스틴베스트 E"])
async def get_all_sustainbest_e(db: Session = Depends(get_db)):
    """모든 서스틴베스트 E 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_all_sustainbest_e()
        return {
            "success": True,
            "message": "서스틴베스트 E 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sustainbest-e/category/{kpi_category_e}", tags=["서스틴베스트 E"])
async def get_sustainbest_e_by_category(
    kpi_category_e: str,
    db: Session = Depends(get_db)
):
    """KPI 카테고리별 서스틴베스트 E 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_sustainbest_e_by_category(kpi_category_e)
        return {
            "success": True,
            "message": f"KPI 카테고리 '{kpi_category_e}' 서스틴베스트 E 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sustainbest-e/categories", tags=["서스틴베스트 E"])
async def get_sustainbest_e_categories(db: Session = Depends(get_db)):
    """서스틴베스트 E KPI 카테고리 목록 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_sustainbest_e_categories()
        return {
            "success": True,
            "message": "서스틴베스트 E KPI 카테고리 목록 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sustainbest S Table Controllers
@router.get("/sustainbest-s", tags=["서스틴베스트 S"])
async def get_all_sustainbest_s(db: Session = Depends(get_db)):
    """모든 서스틴베스트 S 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_all_sustainbest_s()
        return {
            "success": True,
            "message": "서스틴베스트 S 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sustainbest-s/category/{kpi_category_s}", tags=["서스틴베스트 S"])
async def get_sustainbest_s_by_category(
    kpi_category_s: str,
    db: Session = Depends(get_db)
):
    """KPI 카테고리별 서스틴베스트 S 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_sustainbest_s_by_category(kpi_category_s)
        return {
            "success": True,
            "message": f"KPI 카테고리 '{kpi_category_s}' 서스틴베스트 S 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sustainbest-s/categories", tags=["서스틴베스트 S"])
async def get_sustainbest_s_categories(db: Session = Depends(get_db)):
    """서스틴베스트 S KPI 카테고리 목록 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_sustainbest_s_categories()
        return {
            "success": True,
            "message": "서스틴베스트 S KPI 카테고리 목록 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sustainbest G Table Controllers
@router.get("/sustainbest-g", tags=["서스틴베스트 G"])
async def get_all_sustainbest_g(db: Session = Depends(get_db)):
    """모든 서스틴베스트 G 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_all_sustainbest_g()
        return {
            "success": True,
            "message": "서스틴베스트 G 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sustainbest-g/category/{kpi_category_g}", tags=["서스틴베스트 G"])
async def get_sustainbest_g_by_category(
    kpi_category_g: str,
    db: Session = Depends(get_db)
):
    """KPI 카테고리별 서스틴베스트 G 데이터 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_sustainbest_g_by_category(kpi_category_g)
        return {
            "success": True,
            "message": f"KPI 카테고리 '{kpi_category_g}' 서스틴베스트 G 데이터 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sustainbest-g/categories", tags=["서스틴베스트 G"])
async def get_sustainbest_g_categories(db: Session = Depends(get_db)):
    """서스틴베스트 G KPI 카테고리 목록 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_sustainbest_g_categories()
        return {
            "success": True,
            "message": "서스틴베스트 G KPI 카테고리 목록 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 통합 검색 Controller
@router.get("/search", tags=["검색"])
async def search_materiality_data(
    keyword: str = Query(..., description="검색할 키워드"),
    table_type: str = Query("all", description="검색할 테이블 타입 (all, category, kcgs, sasb, sustainbest_e, sustainbest_s, sustainbest_g)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """키워드로 모든 테이블에서 검색"""
    try:
        service = MaterialityService(db)
        data = service.search_materiality_data(keyword, table_type)
        return {
            "success": True,
            "message": f"키워드 '{keyword}' 검색 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 통계 정보 Controller
@router.get("/statistics", tags=["통계"])
async def get_materiality_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Materiality 데이터 통계 정보 조회"""
    try:
        service = MaterialityService(db)
        data = service.get_materiality_statistics()
        return {
            "success": True,
            "message": "Materiality 데이터 통계 정보 조회 완료",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
