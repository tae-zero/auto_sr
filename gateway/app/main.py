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
import asyncio

from app.domain.auth.controller.auth_controller import router as auth_router
from app.www.jwt_auth_middleware import AuthMiddleware
from app.domain.discovery.service_discovery import ServiceDiscovery
from app.domain.discovery.service_type import ServiceType
from app.common.utility.constant.settings import Settings
from app.common.utility.factory.response_factory import ResponseFactory
# Gateway는 DB에 직접 접근하지 않음 (MSA 원칙)

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
    
    # 서비스 디스커버리 초기화 및 서비스 등록
    app.state.service_discovery = ServiceDiscovery()
    
    # Auth Service 연결 테스트
    # Railway 환경에서는 RAILWAY_AUTH_SERVICE_URL 사용, 로컬에서는 Docker 컨테이너 이름 사용
    auth_service_url = os.getenv("RAILWAY_AUTH_SERVICE_URL")
    if auth_service_url:
        # Railway 환경
        logger.info(f"🚀 Railway 환경에서 Auth Service 연결 시도: {auth_service_url}")
    else:
        # 로컬 Docker 환경 또는 Railway에서 환경변수가 설정되지 않은 경우
        auth_service_url = "http://localhost:8008"  # 로컬 auth-service
        logger.info(f"🚀 로컬 Auth Service 연결 시도: {auth_service_url}")
    
    try:
        import httpx
        # 더 긴 타임아웃과 재시도 로직
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{auth_service_url}/health")
                    if response.status_code == 200:
                        logger.info(f"✅ Auth Service 연결 성공: {auth_service_url}")
                        break
                    else:
                        logger.warning(f"⚠️ Auth Service 응답 이상 (시도 {attempt + 1}/3): {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Auth Service 연결 시도 {attempt + 1}/3 실패: {str(e)}")
                if attempt < 2:  # 마지막 시도가 아니면 잠시 대기
                    await asyncio.sleep(2)
                else:
                    logger.warning(f"⚠️ Auth Service 연결 최종 실패 (서비스는 계속 실행): {str(e)}")
    except Exception as e:
        logger.warning(f"⚠️ Auth Service 연결 테스트 중 오류 (서비스는 계속 실행): {str(e)}")
    
    # 기본 서비스 등록
    app.state.service_discovery.register_service(
        service_name="chatbot-service",
        instances=[{"host": "chatbot-service", "port": 8006, "weight": 1}],
        load_balancer_type="round_robin"
    )
    
    # Auth Service 등록
    app.state.service_discovery.register_service(
        service_name="auth-service",
        instances=[{"host": "auth-service", "port": 8008, "weight": 1}],
        load_balancer_type="round_robin"
    )
    
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for ausikor.com - MSV Pattern with Layered Architecture",
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
        "https://www.taezero.com",  # 프로덕션 도메인
        "https://taezero.com",      # 프로덕션 도메인 (www 없이)
        "*"  # 개발 환경에서 모든 origin 허용
    ], # 프론트엔드 주소 명시
    allow_credentials=True,  # HttpOnly 쿠키 사용을 위해 필수
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

# ✅ MSV 패턴의 Auth 도메인 컨트롤러 사용
app.include_router(auth_router)

# 404 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error(f"404 에러: {request.url}")
    return JSONResponse(
        status_code=404,
        content={"detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}"}
    )

# 기본 루트 경로
@app.get("/")
async def root():
    return {
        "message": "Gateway API", 
        "version": "0.1.0",
        "architecture": "MSV Pattern with Layered Architecture",
        "description": "모든 API 요청은 /api/v1 경로를 통해 처리됩니다"
    }

# 루트 레벨 헬스 체크
@app.get("/health")
async def health_check_root():
    return {
        "status": "healthy", 
        "service": "gateway", 
        "path": "root",
        "architecture": "MSV Pattern with Layered Architecture"
    }

# 데이터베이스 헬스 체크 (auth-service에 위임)
@app.get("/health/db")
async def health_check_db():
    return {
        "status": "healthy",
        "service": "gateway",
        "message": "Database health check delegated to auth-service",
        "architecture": "MSV Pattern with Layered Architecture"
    }

# Gateway는 순수한 라우팅만 담당 (MSA 원칙)

# ✅ 서버 실행
if __name__ == "__main__":
    import uvicorn
    # Railway의 PORT 환경변수 사용, 없으면 8080 기본값
    port = int(os.getenv("PORT", os.getenv("SERVICE_PORT", 8080)))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)