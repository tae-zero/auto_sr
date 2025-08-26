from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile
from fastapi.responses import JSONResponse
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from ..common.config import FAISS_VOLUME_PATH, MAX_FILE_SIZE
from ..common.schemas import (
    SearchRequest, SearchResponse, DraftRequest, DraftResponse,
    PolishRequest, PolishResponse, DraftAndPolishRequest, DraftAndPolishResponse,
    UploadResponse, ErrorResponse
)
from ..common.utils import generate_request_id, log_request_info, log_response_info, timing_decorator
from ..www.security import verify_admin_token
from ..domain.rag.rag_manager import RAGManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG"])

# RAG 매니저 인스턴스
rag_manager = RAGManager()

@router.get("/services")
async def get_available_services():
    """사용 가능한 RAG 서비스 목록을 반환합니다."""
    request_id = generate_request_id()
    log_request_info(request_id, "GET", "/rag/services")
    
    try:
        services = rag_manager.get_available_services()
        status = rag_manager.get_service_status()
        
        response_data = {
            "available_services": services,
            "service_status": status
        }
        
        log_response_info(request_id, 200, response_data)
        return response_data
        
    except Exception as e:
        logger.error(f"서비스 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
@timing_decorator
async def search_documents(
    request: SearchRequest,
    service: Optional[str] = Query(None, description="사용할 RAG 서비스 (openai, huggingface)")
):
    """문서를 검색합니다."""
    request_id = generate_request_id()
    log_request_info(request_id, "POST", "/rag/search", {"query": request.question, "top_k": request.top_k, "service": service})
    
    try:
        # 서비스 검증
        if service and not rag_manager.is_service_available(service):
            raise HTTPException(status_code=400, detail=f"서비스 {service}를 사용할 수 없습니다")
        
        # 검색 수행
        hits, context = rag_manager.search(
            query=request.question,
            top_k=request.top_k,
            service_name=service
        )
        
        response_data = SearchResponse(
            hits=hits,
            context=context,
            service_used=service or "default"
        )
        
        log_response_info(request_id, 200, response_data)
        return response_data
        
    except ValueError as e:
        logger.error(f"검색 요청 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"검색 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/draft")
@timing_decorator
async def generate_draft(
    request: DraftRequest,
    service: Optional[str] = Query(None, description="사용할 RAG 서비스 (openai, huggingface)")
):
    """섹션별 초안을 생성합니다."""
    request_id = generate_request_id()
    log_request_info(request_id, "POST", "/rag/draft", {"question": request.question, "sections": request.sections, "service": service})
    
    try:
        # 서비스 검증
        if service and not rag_manager.is_service_available(service):
            raise HTTPException(status_code=400, detail=f"서비스 {service}를 사용할 수 없습니다")
        
        # 초안 생성
        draft_content = rag_manager.generate_draft(
            question=request.question,
            sections=request.sections,
            top_k=request.top_k,
            service_name=service
        )
        
        response_data = DraftResponse(
            draft=draft_content,
            service_used=service or "default"
        )
        
        log_response_info(request_id, 200, response_data)
        return response_data
        
    except Exception as e:
        logger.error(f"초안 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/polish")
@timing_decorator
async def polish_text(
    request: PolishRequest,
    service: Optional[str] = Query(None, description="사용할 RAG 서비스 (openai, huggingface)")
):
    """텍스트를 윤문합니다."""
    request_id = generate_request_id()
    log_request_info(request_id, "POST", "/rag/polish", {"text_length": len(request.text), "tone": request.tone, "service": service})
    
    try:
        # 서비스 검증
        if service and not rag_manager.is_service_available(service):
            raise HTTPException(status_code=400, detail=f"서비스 {service}를 사용할 수 없습니다")
        
        # 윤문 수행
        polished_text = rag_manager.polish_text(
            text=request.text,
            tone=request.tone,
            style_guide=request.style_guide,
            service_name=service
        )
        
        response_data = PolishResponse(
            polished=polished_text,
            service_used=service or "default"
        )
        
        log_response_info(request_id, 200, response_data)
        return response_data
        
    except Exception as e:
        logger.error(f"윤문 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/draft-and-polish")
@timing_decorator
async def draft_and_polish(
    request: DraftAndPolishRequest,
    service: Optional[str] = Query(None, description="사용할 RAG 서비스 (openai, huggingface)")
):
    """초안 생성과 윤문을 순차적으로 수행합니다."""
    request_id = generate_request_id()
    log_request_info(request_id, "POST", "/rag/draft-and-polish", {"question": request.question, "sections": request.sections, "service": service})
    
    try:
        # 서비스 검증
        if service and not rag_manager.is_service_available(service):
            raise HTTPException(status_code=400, detail=f"서비스 {service}를 사용할 수 없습니다")
        
        # 1단계: 초안 생성
        draft_content = rag_manager.generate_draft(
            question=request.question,
            sections=request.sections,
            top_k=request.top_k,
            service_name=service
        )
        
        # 2단계: 윤문 수행
        polished_text = rag_manager.polish_text(
            text=draft_content,
            tone=request.tone,
            style_guide=request.style_guide,
            service_name=service
        )
        
        response_data = DraftAndPolishResponse(
            draft=draft_content,
            polished=polished_text,
            service_used=service or "default"
        )
        
        log_response_info(request_id, 200, response_data)
        return response_data
        
    except Exception as e:
        logger.error(f"초안+윤문 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/faiss/upload", dependencies=[Depends(verify_admin_token)])
async def upload_faiss_files(
    index_file: UploadFile,
    store_file: UploadFile
):
    """FAISS 인덱스와 문서 스토어 파일을 업로드합니다."""
    request_id = generate_request_id()
    log_request_info(request_id, "POST", "/rag/faiss/upload", {"index_size": index_file.size, "store_size": store_file.size})
    
    try:
        from ..common.utils import ensure_directory_exists, validate_file_size, format_file_size
        
        # 디렉토리 확인/생성
        ensure_directory_exists(FAISS_VOLUME_PATH)
        
        # 파일 크기 검증
        if not validate_file_size(index_file.filename, MAX_FILE_SIZE):
            raise HTTPException(status_code=400, detail="인덱스 파일 크기가 너무 큽니다")
        
        if not validate_file_size(store_file.filename, MAX_FILE_SIZE):
            raise HTTPException(status_code=400, detail="스토어 파일 크기가 너무 큽니다")
        
        # 파일 저장
        index_path = Path(FAISS_VOLUME_PATH) / "my_index.faiss"
        store_path = Path(FAISS_VOLUME_PATH) / "doc_store.pkl"
        
        with open(index_path, "wb") as f:
            f.write(index_file.file.read())
        
        with open(store_path, "wb") as f:
            f.write(store_file.file.read())
        
        # 파일 크기 확인
        index_size = index_path.stat().st_size
        store_size = store_path.stat().st_size
        
        # 모든 RAG 서비스의 인덱스 재로딩
        load_results = rag_manager.load_all_indices()
        
        response_data = UploadResponse(
            ok=True,
            size={"index_bytes": index_size, "store_bytes": store_size},
            load_results=load_results
        )
        
        log_response_info(request_id, 200, response_data)
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"FAISS 파일 업로드 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
