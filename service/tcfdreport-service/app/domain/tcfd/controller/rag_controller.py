"""
RAG 컨트롤러 - 임베딩 및 검색 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

# Pydantic 모델들
class SearchRequest(BaseModel):
    query: str
    k: int = 5
    filters: Optional[Dict[str, Any]] = None
    collection: Optional[str] = None  # "sr_corpus", "standards", "all"

class SearchResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None

class SearchResponse(BaseModel):
    query: str
    results: Dict[str, List[SearchResult]]
    total_results: int

class CollectionInfo(BaseModel):
    collection_name: str
    document_count: int
    status: str

class EmbeddingStatus(BaseModel):
    initialized: bool
    collections: List[CollectionInfo]
    message: str

@router.get("/status", response_model=EmbeddingStatus)
async def get_embedding_status(request):
    """임베딩 상태 조회"""
    try:
        rag_service = request.app.state.rag_service
        
        if not rag_service:
            return EmbeddingStatus(
                initialized=False,
                collections=[],
                message="RAG 서비스가 초기화되지 않았습니다."
            )
        
        collection_info = await rag_service.get_collection_info()
        
        collections = []
        for name, info in collection_info.items():
            collections.append(CollectionInfo(
                collection_name=name,
                document_count=info["document_count"],
                status=info["status"]
            ))
        
        return EmbeddingStatus(
            initialized=True,
            collections=collections,
            message="RAG 서비스가 정상적으로 초기화되었습니다."
        )
        
    except Exception as e:
        logger.error(f"임베딩 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def search_documents(search_request: SearchRequest, request):
    """문서 검색"""
    try:
        rag_service = request.app.state.rag_service
        
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG 서비스가 초기화되지 않았습니다.")
        
        # 검색 실행
        if search_request.collection == "sr_corpus":
            results = {
                "sr_corpus": await rag_service.search_sr_corpus(
                    search_request.query, 
                    search_request.k, 
                    search_request.filters
                )
            }
        elif search_request.collection == "standards":
            results = {
                "standards": await rag_service.search_standards(
                    search_request.query, 
                    search_request.k, 
                    search_request.filters
                )
            }
        else:
            # 모든 컬렉션에서 검색
            results = await rag_service.search_all(
                search_request.query, 
                search_request.k, 
                search_request.filters
            )
        
        # 응답 형식 변환
        formatted_results = {}
        total_results = 0
        
        for collection_name, docs in results.items():
            formatted_docs = []
            for doc in docs:
                formatted_docs.append(SearchResult(
                    content=doc.page_content,
                    metadata=doc.metadata,
                    score=getattr(doc, 'score', None)
                ))
            formatted_results[collection_name] = formatted_docs
            total_results += len(formatted_docs)
        
        return SearchResponse(
            query=search_request.query,
            results=formatted_results,
            total_results=total_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"문서 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"검색 오류: {str(e)}")

@router.post("/search/sr")
async def search_sr_corpus(search_request: SearchRequest, request):
    """SR 코퍼스에서만 검색"""
    search_request.collection = "sr_corpus"
    return await search_documents(search_request, request)

@router.post("/search/standards")
async def search_standards(search_request: SearchRequest, request):
    """TCFD Standards에서만 검색"""
    search_request.collection = "standards"
    return await search_documents(search_request, request)

@router.post("/reinitialize")
async def reinitialize_embeddings(request):
    """임베딩 재초기화"""
    try:
        rag_service = request.app.state.rag_service
        
        if not rag_service:
            raise HTTPException(status_code=503, detail="RAG 서비스가 초기화되지 않았습니다.")
        
        success = await rag_service.initialize_embeddings()
        
        if success:
            return {"message": "임베딩 재초기화가 완료되었습니다.", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="임베딩 재초기화에 실패했습니다.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"임베딩 재초기화 실패: {e}")
        raise HTTPException(status_code=500, detail=f"재초기화 오류: {str(e)}")
