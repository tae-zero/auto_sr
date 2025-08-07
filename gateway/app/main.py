"""
gateway-router 메인 파일
"""
from typing import Optional, List
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import Request
import uvicorn

from app.router.auth_router import router as auth_router
from app.www.jwt_auth_middleware import AuthMiddleware
from app.domain.discovery.service_discovery import ServiceDiscovery
from app.domain.discovery.service_type import ServiceType
from app.common.utility.constant.settings import Settings
from app.common.utility.factory.response_factory import ResponseFactory

if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gateway_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")
    # Settings 초기화 및 앱 state에 등록
    app.state.settings = Settings()
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for ausikor.com",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 로컬 접근
        "http://127.0.0.1:3000",  # 로컬 IP 접근
        "http://frontend:3000",   # Docker 내부 네트워크
    ], # 프론트엔드 주소 명시
    allow_credentials=True,  # HttpOnly 쿠키 사용을 위해 필수
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

gateway_router = APIRouter(prefix="/api/v1", tags=["Gateway API"])
gateway_router.include_router(auth_router)
# 필요시: gateway_router.include_router(user_router)
app.include_router(gateway_router)

# 🪡🪡🪡 파일이 필요한 서비스 목록 (현재는 없음)
FILE_REQUIRED_SERVICES = set()
@app.get("/", summary="헬스 체크")
async def health_check():
    return {"환영":"합니다"}
# 루트 레벨 엔드포인트들 (인증 미들웨어 적용 안함)
@app.get("/health", summary="헬스 체크")
async def health_check():
    return {"status": "healthy", "service": "gateway"}

@app.get("/login", summary="로그인 페이지")
async def login_page():
    return {"message": "로그인 페이지", "status": "success"}

@app.post("/login", summary="로그인 처리")
async def login_process():
    return {"message": "로그인 처리 완료", "status": "success"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
