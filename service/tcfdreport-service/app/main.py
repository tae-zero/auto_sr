"""
TCFD Report Service - LangChain 기반 AI 보고서 생성
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# RAG 서비스 import (조건부)
try:
    from app.domain.tcfd.rag_service import RAGService
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAG 서비스 사용 불가: chromadb 등 필요한 패키지가 설치되지 않음")

# 데이터베이스 import
from app.common.database.database import database
from app.common.database.init_tables import init_tables

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
    
    # 데이터베이스 연결 초기화
    try:
        await database.connect()
        logger.info("✅ 데이터베이스 연결 초기화 완료")
        
        # 데이터베이스 테이블 초기화
        database_url = os.getenv("DATABASE_URL")
        if database_url:
            table_init_success = await init_tables(database_url)
            if table_init_success:
                logger.info("✅ 데이터베이스 테이블 초기화 완료")
            else:
                logger.warning("⚠️ 데이터베이스 테이블 초기화 실패")
        else:
            logger.warning("⚠️ DATABASE_URL 환경변수가 설정되지 않음")
            
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 초기화 실패: {str(e)}")
    
    # RAG 서비스 초기화 (조건부)
    if RAG_AVAILABLE:
        try:
            app.state.rag_service = RAGService()
            rag_initialized = await app.state.rag_service.initialize_embeddings()
            if rag_initialized:
                logger.info("✅ RAG 서비스 초기화 완료")
            else:
                logger.warning("⚠️ RAG 서비스 초기화 실패")
                
        except Exception as e:
            logger.error(f"❌ RAG 서비스 초기화 실패: {str(e)}")
    else:
        logger.warning("⚠️ RAG 서비스 사용 불가: 필요한 패키지가 설치되지 않음")
    
    yield
    
    # 리소스 정리
    logger.info("🛑 TCFD Report Service 종료")
    
    # 데이터베이스 연결 해제
    try:
        await database.disconnect()
        logger.info("✅ 데이터베이스 연결 해제 완료")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 해제 실패: {str(e)}")
    
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

# RAG 라우터 포함 (조건부)
try:
    from app.domain.tcfd.controller.rag_controller import router as rag_router
    app.include_router(rag_router)
except ImportError:
    print("⚠️ RAG 라우터 사용 불가: 필요한 패키지가 설치되지 않음")

# TCFD 입력 데이터 라우터 포함
try:
    from app.domain.tcfd.controller.tcfd_input_controller import router as tcfd_input_router
    app.include_router(tcfd_input_router)
    print("✅ TCFD 입력 데이터 라우터 로드 완료")
except ImportError as e:
    print(f"⚠️ TCFD 입력 데이터 라우터 사용 불가: {str(e)}")

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
    # Railway 환경에서는 PORT 환경변수 사용, 로컬에서는 8004 사용
    if os.getenv("RAILWAY_ENVIRONMENT") == "true":
        port = int(os.getenv("PORT", 8004))
    else:
        port = 8004
    uvicorn.run(app, host="0.0.0.0", port=port)
