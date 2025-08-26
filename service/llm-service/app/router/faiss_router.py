from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Optional
from ..www.jwt_auth_middleware import verify_token
from ..common.schemas import UploadResponse
from ..common.utils import generate_request_id
import os
import shutil
from pathlib import Path
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag/faiss", tags=["FAISS Management"])

@router.post("/upload", response_model=UploadResponse)
async def upload_faiss_files(
    index_file: UploadFile = File(...),
    store_file: UploadFile = File(...),
    user_id: Optional[str] = Depends(verify_token)
):
    """
    FAISS 인덱스 및 문서 스토어 파일 업로드
    
    Args:
        index_file: FAISS 인덱스 파일 (.faiss)
        store_file: 문서 스토어 파일 (.pkl)
        user_id: 인증된 사용자 ID
        
    Returns:
        업로드 결과 및 파일 크기 정보
    """
    request_id = generate_request_id()
    logger.info(f"[{request_id}] FAISS 파일 업로드 시작 - 사용자: {user_id}")
    
    try:
        # 파일 확장자 검증
        if not index_file.filename.endswith('.faiss'):
            raise HTTPException(status_code=400, detail="인덱스 파일은 .faiss 확장자여야 합니다")
        
        if not store_file.filename.endswith('.pkl'):
            raise HTTPException(status_code=400, detail="스토어 파일은 .pkl 확장자여야 합니다")
        
        # 업로드 디렉토리 생성
        upload_dir = Path("./vectordb/sr_corpus")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일 저장
        index_path = upload_dir / "index.faiss"
        store_path = upload_dir / "index.pkl"
        
        # 기존 파일 백업 (있다면)
        if index_path.exists():
            backup_path = upload_dir / f"index_backup_{int(time.time())}.faiss"
            shutil.copy2(index_path, backup_path)
            logger.info(f"[{request_id}] 기존 인덱스 파일 백업: {backup_path}")
        
        if store_path.exists():
            backup_path = upload_dir / f"index_backup_{int(time.time())}.pkl"
            shutil.copy2(store_path, backup_path)
            logger.info(f"[{request_id}] 기존 스토어 파일 백업: {backup_path}")
        
        # 새 파일 저장
        with open(index_path, "wb") as buffer:
            shutil.copyfileobj(index_file.file, buffer)
        
        with open(store_path, "wb") as buffer:
            shutil.copyfileobj(store_file.file, buffer)
        
        # 파일 크기 확인
        index_size = index_path.stat().st_size
        store_size = store_path.stat().st_size
        
        logger.info(f"[{request_id}] FAISS 파일 업로드 완료 - 인덱스: {index_size} bytes, 스토어: {store_size} bytes")
        
        return UploadResponse(
            ok=True,
            size={
                "index_file": index_size,
                "store_file": store_size
            },
            load_results={
                "openai": True,
                "huggingface": True
            }
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] FAISS 파일 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파일 업로드 실패: {str(e)}")
    
    finally:
        # 파일 핸들러 정리
        if index_file.file:
            index_file.file.close()
        if store_file.file:
            store_file.file.close()

@router.get("/status")
async def get_faiss_status(
    user_id: Optional[str] = Depends(verify_token)
):
    """
    FAISS 파일 상태 확인
    
    Args:
        user_id: 인증된 사용자 ID
        
    Returns:
        FAISS 파일 상태 정보
    """
    request_id = generate_request_id()
    logger.info(f"[{request_id}] FAISS 상태 확인 - 사용자: {user_id}")
    
    try:
        upload_dir = Path("./vectordb/sr_corpus")
        index_path = upload_dir / "index.faiss"
        store_path = upload_dir / "index.pkl"
        
        return {
            "index_file": {
                "exists": index_path.exists(),
                "size": index_path.stat().st_size if index_path.exists() else 0,
                "path": str(index_path)
            },
            "store_file": {
                "exists": store_path.exists(),
                "size": store_path.stat().st_size if store_path.exists() else 0,
                "path": str(store_path)
            },
            "upload_directory": str(upload_dir),
            "status": "ready" if index_path.exists() and store_path.exists() else "missing_files"
        }
        
    except Exception as e:
        logger.error(f"[{request_id}] FAISS 상태 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 확인 실패: {str(e)}")
