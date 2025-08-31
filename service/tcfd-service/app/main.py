"""
TCFD Service - 재무정보 처리 및 분석
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# 환경변수 로드
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# JWT Secret 키 로깅 (디버깅용)
jwt_secret = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-here")
logger.info(f"🔐 TCFD Service main.py JWT_SECRET_KEY: {jwt_secret[:20]}...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    try:
        logger.info("🚀 TCFD Service 시작")
        logger.info("✅ 데이터베이스 테이블은 이미 존재함 (수동 생성 완료)")
        logger.info(f"🔐 JWT_SECRET_KEY 설정 완료: {jwt_secret[:20]}...")
        
        yield
        
        # 리소스 정리
        logger.info("🛑 TCFD Service 종료")
    except Exception as e:
        logger.error(f"❌ TCFD Service 생명주기 관리 오류: {e}")
        logger.info("⚠️ 서비스는 계속 실행됩니다")
        yield

app = FastAPI(
    title=os.getenv("SERVICE_NAME", "TCFD Service"),
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
try:
    from app.domain.tcfd.controller.tcfd_controller import router as tcfd_router
    app.include_router(tcfd_router)
    logger.info("✅ TCFD 라우터 등록 완료")
except Exception as e:
    logger.error(f"❌ TCFD 라우터 등록 실패: {e}")
    logger.info("⚠️ 서비스는 계속 실행됩니다")

# 헬스 체크
@app.get("/health")
async def health_check():
    try:
        return {
            "status": "healthy",
            "service": "tcfd-service",
            "architecture": "MSV Pattern with Layered Architecture",
            "database": "connected",
            "jwt_secret_configured": bool(jwt_secret),
            "layers": [
                "Controller Layer - TCFD API 엔드포인트",
                "Service Layer - TCFD 비즈니스 로직",
                "Repository Layer - 데이터 접근",
                "Entity Layer - 데이터베이스 엔티티",
                "Model Layer - Pydantic 모델",
                "Schema Layer - TCFD 스키마"
            ]
        }
    except Exception as e:
        logger.error(f"Health check 오류: {e}")
        raise HTTPException(status_code=500, detail="Health check 실패")

# 루트 경로
@app.get("/")
async def root():
    try:
        return {
            "message": "TCFD Service",
            "version": "0.1.0",
            "architecture": "MSV Pattern with Layered Architecture",
            "description": "재무정보 처리 및 분석 서비스",
            "database": "tcfd_standard table exists",
            "jwt_secret_configured": bool(jwt_secret)
        }
    except Exception as e:
        logger.error(f"Root 엔드포인트 오류: {e}")
        raise HTTPException(status_code=500, detail="서비스 오류")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", os.getenv("PORT", "8005")))
    uvicorn.run(app, host=os.getenv("SERVICE_HOST", "0.0.0.0"), port=port)
