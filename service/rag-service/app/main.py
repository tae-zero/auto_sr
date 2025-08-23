from fastapi import FastAPI, HTTPException
from .query import router as rag_router
from .ingest import router as ingest_router
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=os.getenv("SERVICE_NAME", "RAG Service (FAISS + LangChain)"),
    version="1.0.0",
    description="RAG (Retrieval-Augmented Generation) 서비스 - FAISS + LangChain 기반"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계라면 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 초기화 작업"""
    try:
        logger.info("🚀 RAG Service 시작")
        logger.info("✅ RAG Service 초기화 완료")
    except Exception as e:
        logger.error(f"❌ RAG Service 초기화 실패: {e}")
        logger.info("⚠️ 서비스는 계속 실행됩니다")

@app.get("/health")
def health():
    try:
        return {
            "status": "healthy",
            "service": os.getenv("SERVICE_NAME", "rag-service"),
            "architecture": "RAG Service with FAISS + LangChain"
        }
    except Exception as e:
        logger.error(f"Health check 오류: {e}")
        raise HTTPException(status_code=500, detail="Health check 실패")

@app.get("/")
async def root():
    return {
        "message": "RAG Service",
        "version": "1.0.0",
        "description": "RAG (Retrieval-Augmented Generation) 서비스",
        "architecture": "FAISS + LangChain 기반"
    }

# 라우터 등록
try:
    app.include_router(rag_router)
    app.include_router(ingest_router)
    logger.info("✅ RAG Service 라우터 등록 완료")
except Exception as e:
    logger.error(f"❌ RAG Service 라우터 등록 실패: {e}")
    logger.info("⚠️ 서비스는 계속 실행됩니다")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", os.getenv("PORT", "8002")))
    uvicorn.run(app, host=os.getenv("SERVICE_HOST", "0.0.0.0"), port=port)
