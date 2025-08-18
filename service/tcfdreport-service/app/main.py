"""
TCFD Report Service - LangChain 기반 AI 보고서 생성
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# RAG 서비스 import
from app.domain.tcfd.rag_service import RAGService

# 환경변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🚀 TCFD Report Service 시작")
    
    # RAG 서비스 초기화
    try:
        app.state.rag_service = RAGService()
        rag_initialized = await app.state.rag_service.initialize_embeddings()
        if rag_initialized:
            logger.info("✅ RAG 서비스 초기화 완료")
        else:
            logger.warning("⚠️ RAG 서비스 초기화 실패")
            
    except Exception as e:
        logger.error(f"❌ RAG 서비스 초기화 실패: {str(e)}")
    
    yield
    
    # 리소스 정리
    logger.info("🛑 TCFD Report Service 종료")
    if hasattr(app.state, 'rag_service'):
        await app.state.rag_service.close()

app = FastAPI(
    title="TCFD Report Service",
    description="AI 기반 TCFD 보고서 생성 서비스 - LangChain 기반",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG 라우터 포함
from app.domain.tcfd.controller.rag_controller import router as rag_router

app.include_router(rag_router)

# 헬스 체크
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "tcfd-report-service",
        "rag_services": "enabled" if hasattr(app.state, 'rag_service') else "disabled",
        "description": "AI 기반 TCFD 보고서 생성 서비스"
    }

# 루트 경로
@app.get("/")
async def root():
    return {
        "message": "TCFD Report Service",
        "version": "0.1.0",
        "description": "AI 기반 TCFD 보고서 생성 서비스",
        "features": [
            "LangChain 기반 문서 분석",
            "AI 보고서 생성",
            "기후 리스크 평가",
            "TCFD 프레임워크 준수"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port)
