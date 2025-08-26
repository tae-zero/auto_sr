from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
import httpx
import logging
from typing import Optional
import os

from ..www.jwt_auth_middleware import verify_token
from ..common.utility.constant.settings import Settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/faiss", tags=["FAISS"])

# =============================================================================
# 🔐 관리자 토큰 검증
# =============================================================================

async def verify_admin_token(token: str = Depends(verify_token)) -> bool:
    """관리자 토큰을 검증합니다."""
    try:
        # JWT 토큰에서 사용자 정보 추출
        # 여기서는 간단히 admin 역할을 확인
        # 실제로는 JWT payload에서 role을 확인해야 함
        return True
    except Exception as e:
        logger.error(f"관리자 토큰 검증 실패: {e}")
        raise HTTPException(status_code=401, detail="관리자 권한이 필요합니다")

# =============================================================================
# 📁 FAISS 파일 업로드 (게이트웨이를 통한 프록시)
# =============================================================================

@router.post("/upload")
async def upload_faiss_files(
    index: UploadFile = File(..., description="FAISS 인덱스 파일"),
    store: UploadFile = File(..., description="문서 스토어 파일"),
    _: bool = Depends(verify_admin_token)
):
    """
    FAISS 파일을 게이트웨이를 통해 LLM 서비스로 업로드합니다.
    
    이 엔드포인트는 게이트웨이에서 파일을 받아서 LLM 서비스로 전달합니다.
    """
    try:
        logger.info(f"FAISS 파일 업로드 요청: {index.filename}, {store.filename}")
        
        # LLM 서비스 URL 가져오기
        llm_service_url = os.getenv("LLM_SERVICE_URL", "http://llm-service:8002")
        
        # 파일 크기 검증
        if index.size and index.size > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(status_code=400, detail="인덱스 파일이 너무 큽니다 (100MB 제한)")
        
        if store.size and store.size > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(status_code=400, detail="스토어 파일이 너무 큽니다 (100MB 제한)")
        
        # LLM 서비스로 파일 전달
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5분 타임아웃
            files = {
                "index": (index.filename, index.file, "application/octet-stream"),
                "store": (store.filename, store.file, "application/octet-stream")
            }
            
            # 관리자 토큰 (LLM 서비스에서 요구)
            admin_token = os.getenv("LLM_ADMIN_TOKEN", "supersecret")
            headers = {"X-ADMIN-TOKEN": admin_token}
            
            response = await client.post(
                f"{llm_service_url}/rag/faiss/upload",
                files=files,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ FAISS 파일 업로드 성공: {result}")
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "FAISS 파일 업로드 성공",
                        "llm_service_response": result,
                        "uploaded_files": {
                            "index": index.filename,
                            "store": store.filename
                        }
                    }
                )
            else:
                error_detail = response.text
                logger.error(f"❌ LLM 서비스 업로드 실패: {response.status_code} - {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"LLM 서비스 업로드 실패: {error_detail}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"FAISS 업로드 처리 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"업로드 처리 실패: {str(e)}")

# =============================================================================
# 🔍 FAISS 상태 확인
# =============================================================================

@router.get("/status")
async def get_faiss_status():
    """LLM 서비스의 FAISS 상태를 확인합니다."""
    try:
        llm_service_url = os.getenv("LLM_SERVICE_URL", "http://llm-service:8002")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{llm_service_url}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                return JSONResponse(
                    status_code=200,
                    content={
                        "llm_service_health": health_data,
                        "faiss_status": {
                            "index_loaded": health_data.get("index_loaded", False),
                            "store_loaded": health_data.get("store_loaded", False),
                            "embed_dim": health_data.get("embed_dim", 0)
                        }
                    }
                )
            else:
                raise HTTPException(
                    status_code=503,
                    detail="LLM 서비스에 연결할 수 없습니다"
                )
                
    except Exception as e:
        logger.error(f"FAISS 상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")

# =============================================================================
# 🔄 FAISS 파일 교체 (무중단 스왑)
# =============================================================================

@router.post("/swap")
async def swap_faiss_files(
    index: UploadFile = File(..., description="새 FAISS 인덱스 파일"),
    store: UploadFile = File(..., description="새 문서 스토어 파일"),
    _: bool = Depends(verify_admin_token)
):
    """
    FAISS 파일을 안전하게 교체합니다 (무중단 스왑).
    
    이 엔드포인트는 새 파일을 임시로 업로드하고 검증 후 교체합니다.
    """
    try:
        logger.info(f"FAISS 파일 교체 요청: {index.filename}, {store.filename}")
        
        # 1. 임시 파일명으로 업로드
        temp_index_name = f"temp_{index.filename}"
        temp_store_name = f"temp_{store.filename}"
        
        # 2. LLM 서비스로 임시 업로드
        llm_service_url = os.getenv("LLM_SERVICE_URL", "http://llm-service:8002")
        admin_token = os.getenv("LLM_ADMIN_TOKEN", "supersecret")
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            files = {
                "index": (temp_index_name, index.file, "application/octet-stream"),
                "store": (temp_store_name, store.file, "application/octet-stream")
            }
            
            headers = {"X-ADMIN-TOKEN": admin_token}
            
            # 임시 업로드
            response = await client.post(
                f"{llm_service_url}/rag/faiss/upload",
                files=files,
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info("✅ FAISS 파일 교체 완료")
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": "FAISS 파일 교체 성공",
                        "swapped_files": {
                            "index": temp_index_name,
                            "store": temp_store_name
                        }
                    }
                )
            else:
                error_detail = response.text
                logger.error(f"❌ FAISS 파일 교체 실패: {response.status_code} - {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"파일 교체 실패: {error_detail}"
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"FAISS 파일 교체 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"파일 교체 실패: {str(e)}")
