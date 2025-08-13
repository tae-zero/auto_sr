"""
TCFD Service - 재무정보 처리 및 분석
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# 환경변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("🚀 TCFD Service 시작")
    
    # 데이터베이스 연결 풀 초기화
    try:
        from app.domain.tcfd.repository.tcfd_repository import TCFDRepository
        app.state.repository = TCFDRepository()
        logger.info("✅ 데이터베이스 연결 풀 초기화 완료")
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 풀 초기화 실패: {str(e)}")
    
    yield
    
    # 리소스 정리
    logger.info("🛑 TCFD Service 종료")
    if hasattr(app.state, 'repository'):
        await app.state.repository.close()

app = FastAPI(
    title="TCFD Service",
    description="재무정보 처리 및 분석 서비스 - MSV Pattern with Layered Architecture",
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

# TCFD 도메인 라우터 포함
from app.domain.tcfd.controller.tcfd_controller import router as tcfd_router
app.include_router(tcfd_router)

# 헬스 체크
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "tcfd-service",
        "architecture": "MSV Pattern with Layered Architecture",
        "ai_services": "disabled",
        "layers": [
            "Controller Layer - TCFD API 엔드포인트",
            "Service Layer - TCFD 비즈니스 로직",
            "Repository Layer - 데이터 접근",
            "Entity Layer - 데이터베이스 엔티티",
            "Model Layer - Pydantic 모델",
            "Schema Layer - TCFD 스키마"
        ]
    }

# 루트 경로
@app.get("/")
async def root():
    return {
        "message": "TCFD Service",
        "version": "0.1.0",
        "architecture": "MSV Pattern with Layered Architecture",
        "description": "재무정보 처리 및 분석 서비스",
        "note": "AI 기능은 TCFD Report Service로 이전되었습니다"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8005))
    uvicorn.run(app, host="0.0.0.0", port=port)
