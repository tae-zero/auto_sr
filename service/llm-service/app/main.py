from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any

from .common.config import SERVICE_NAME, SERVICE_HOST, SERVICE_PORT, EMBED_DIM, FAISS_INDEX_PATH
from .common.schemas import HealthResponse, ErrorResponse
from .common.utils import generate_request_id, log_request_info, log_response_info
from .router.rag_router import router as rag_router
from .router.faiss_router import router as faiss_router
from .router.tcfd_router import tcfd_router
from .domain.rag.rag_manager import RAGManager

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# RAG 매니저 인스턴스
rag_manager = RAGManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시
    logger.info(f"🚀 {SERVICE_NAME} 서비스 시작 중...")
    
    # 모든 RAG 서비스의 인덱스 로딩
    try:
        load_results = rag_manager.load_all_indices()
        logger.info(f"📚 RAG 서비스 인덱스 로딩 결과: {load_results}")
    except Exception as e:
        logger.error(f"❌ RAG 서비스 인덱스 로딩 실패: {e}")
    
    logger.info(f"✅ {SERVICE_NAME} 서비스 시작 완료")
    
    yield
    
    # 종료 시
    logger.info(f"🛑 {SERVICE_NAME} 서비스 종료 중...")

# FastAPI 앱 생성
app = FastAPI(
    title=SERVICE_NAME,
    description=f"2개 RAG 시스템을 지원하는 지속가능경영보고서 분석 서비스 (OpenAI + Hugging Face)",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 미들웨어: 요청/응답 로깅
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = generate_request_id()
    request.state.request_id = request_id
    
    # 요청 로깅
    log_request_info(request_id, f"{request.method} {request.url}")
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # 응답 로깅
    log_response_info(request_id, f"Status {response.status_code}", process_time, process_time=process_time)
    
    return response

# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"[{request_id}] 전역 예외 발생: {exc}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            request_id=request_id
        ).dict()
    )

# =============================================================================
# 🌐 기본 엔드포인트
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """서비스 루트 엔드포인트"""
    return {
        "service": SERVICE_NAME,
        "version": "2.0.0",
        "description": "2개 RAG 시스템을 지원하는 지속가능경영보고서 분석 서비스",
        "architecture": "MSA + MVC (Microservice Architecture + Model-View-Controller)",
        "available_services": ["OpenAI RAG", "Hugging Face RAG"],
        "endpoints": {
            "health": "/health",
            "rag_services": "/rag/services",
            "rag_search": "/rag/search",
            "rag_draft": "/rag/draft",
            "rag_polish": "/rag/polish",
            "rag_draft_and_polish": "/rag/draft-and-polish",
            "faiss_upload": "/rag/faiss/upload"
        }
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """서비스 헬스 체크"""
    try:
        # RAG 서비스 상태 확인
        service_status = rag_manager.get_service_status()
        
        # 전체 상태 계산
        all_loaded = all(status["is_loaded"] for status in service_status.values())
        
        return HealthResponse(
            ok=True,
            service_name=SERVICE_NAME,
            version="2.0.0",
            rag_services=service_status,
            all_services_loaded=all_loaded,
            embed_dim=EMBED_DIM,
            timestamp=time.time()
        )
        
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return HealthResponse(
            ok=False,
            service_name=SERVICE_NAME,
            version="2.0.0",
            error=str(e),
            rag_services={},
            all_services_loaded=False,
            embed_dim=EMBED_DIM,
            timestamp=time.time()
        )

# =============================================================================
# 🔗 라우터 등록
# =============================================================================

# RAG 라우터 등록
app.include_router(rag_router)

# FAISS 라우터 등록
app.include_router(faiss_router)

# TCFD 라우터 등록
app.include_router(tcfd_router)

# 서비스 초기화 완료 (lifespan에서 처리됨)
