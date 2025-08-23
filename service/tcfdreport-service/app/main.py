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
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    try:
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
            logger.info("⚠️ 데이터베이스 없이 서비스가 시작됩니다")
        
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
                logger.info("⚠️ RAG 서비스 없이 서비스가 시작됩니다")
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
            try:
                await app.state.rag_service.close()
                logger.info("✅ RAG 서비스 리소스 정리 완료")
            except Exception as e:
                logger.error(f"❌ RAG 서비스 리소스 정리 실패: {str(e)}")
                
    except Exception as e:
        logger.error(f"❌ TCFD Report Service 생명주기 관리 오류: {e}")
        logger.info("⚠️ 서비스는 계속 실행됩니다")
        yield

app = FastAPI(
    title="TCFD Report Service",
    description="AI 기반 TCFD 보고서 생성 서비스 - LangChain 기반",
    version="1.0.0",
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

# 헬스 체크
@app.get("/health")
async def health_check():
    try:
        return {
            "status": "healthy",
            "service": "tcfd-report-service",
            "architecture": "AI 기반 TCFD 보고서 생성 서비스",
            "rag_available": RAG_AVAILABLE,
            "database_connected": hasattr(app.state, 'database')
        }
    except Exception as e:
        logger.error(f"Health check 오류: {e}")
        raise HTTPException(status_code=500, detail="Health check 실패")

# 루트 경로
@app.get("/")
async def root():
    try:
        return {
            "message": "TCFD Report Service",
            "version": "1.0.0",
            "description": "AI 기반 TCFD 보고서 생성 서비스",
            "architecture": "LangChain 기반",
            "rag_available": RAG_AVAILABLE
        }
    except Exception as e:
        logger.error(f"Root 엔드포인트 오류: {e}")
        raise HTTPException(status_code=500, detail="서비스 오류")

# 라우터 등록
try:
    from app.router import tcfdreport_router
    app.include_router(tcfdreport_router, prefix="/api/v1/tcfdreport")
    logger.info("✅ TCFD Report 라우터 등록 완료")
except Exception as e:
    logger.error(f"❌ TCFD Report 라우터 등록 실패: {e}")
    logger.info("⚠️ 서비스는 계속 실행됩니다")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", os.getenv("PORT", "8004")))
    uvicorn.run(app, host=os.getenv("SERVICE_HOST", "0.0.0.0"), port=port)
