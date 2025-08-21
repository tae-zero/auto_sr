"""
Auth 서비스 메인 애플리케이션 진입점
"""
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

# SQLAlchemy AsyncSession 강제 import
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    print("✅ AsyncSession import 성공")
except ImportError as e:
    print(f"❌ AsyncSession import 실패: {e}")
    # 대체 방법
    import sqlalchemy.ext.asyncio
    AsyncSession = sqlalchemy.ext.asyncio.AsyncSession
    print("✅ AsyncSession 대체 import 성공")

# 환경 변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

# Railway 환경변수 처리
PORT = os.getenv("PORT", os.getenv("SERVICE_PORT", "8008"))
if not PORT.isdigit():
    PORT = "8008"

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("auth_service")

# DB 관련 import
from app.common.database.database import get_db, create_tables, test_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Auth Service 시작")

    # Railway PostgreSQL 연결 대기 (시간 단축)
    import asyncio
    await asyncio.sleep(2)  # 연결 대기 시간 증가

    # Railway 데이터베이스 연결 테스트
    try:
        db_connected = await test_connection()
        if db_connected:
            # 환경변수로 초기화 제어 (기본값: False - Railway에서는 처음에 false로 설정)
            should_init_db = os.getenv("INIT_DATABASE", "false").lower() == "true"
            if should_init_db:
                # 테이블 생성
                await create_tables()
                logger.info("✅ Railway 데이터베이스 초기화 완료")
            else:
                logger.info("ℹ️ Railway 데이터베이스 초기화가 비활성화되었습니다.")
        else:
            logger.warning("⚠️ Railway 데이터베이스 연결 실패 - 서비스는 계속 실행됩니다")
    except Exception as e:
        logger.warning(f"⚠️ 데이터베이스 초기화 중 오류 (서비스는 계속 실행): {str(e)}")
        logger.warning("⚠️ 데이터베이스 연결 없이 서비스가 시작됩니다")
    
    # 서비스 시작 완료 로그
    logger.info("✅ Auth Service 시작 완료 - Health endpoint 사용 가능")
    
    yield
    logger.info("🛑 Auth Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title=os.getenv("SERVICE_NAME", "Auth Service"),
    description="Authentication and Authorization Service - MSV Pattern with Layered Architecture",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 로컬 접근
        "http://localhost:3001",  # 로컬 접근 (포트 3001)
        "http://127.0.0.1:3000",  # 로컬 IP 접근
        "http://127.0.0.1:3001",  # 로컬 IP 접근 (포트 3001)
        "http://frontend:3000",   # Docker 내부 네트워크
        "https://www.taezero.com",  # 프로덕션 도메인
        "https://taezero.com",      # 프로덕션 도메인 (www 없이)
        "https://auth-service-production-1deb.up.railway.app",  # Railway auth-service
        "https://*.up.railway.app",  # Railway 모든 서브도메인
        "https://*.railway.app",     # Railway 모든 도메인
        "*"  # 개발 환경에서 모든 origin 허용
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # CORS preflight 캐시 시간 (24시간)
)

# ✅ MSV 패턴의 Auth 도메인 컨트롤러 사용
from app.domain.auth.controller.auth_controller import router as auth_router
app.include_router(auth_router)

# 기본 루트 경로
@app.get("/")
async def root():
    return {
        "message": "Auth Service", 
        "version": "0.1.0",
        "architecture": "MSV Pattern with Layered Architecture",
        "description": "인증 및 권한 관리 서비스"
    }

# 루트 레벨 헬스 체크
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "auth-service",
        "architecture": "MSV Pattern with Layered Architecture"
    }

# 테스트 엔드포인트
@app.get("/test")
async def test():
    return {
        "message": "Auth Service Test Endpoint", 
        "status": "success",
        "architecture": "MSV Pattern with Layered Architecture"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(PORT)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)