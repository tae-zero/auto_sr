"""
TCFD Report Service - LangChain 기반 AI 보고서 생성
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# LangChain 서비스들 import
from app.domain.tcfd.analysis_service import TCFDAnalysisService
from app.domain.tcfd.report_service import TCFDReportService
from app.domain.tcfd.risk_assessment_service import RiskAssessmentService

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
    
    # AI 서비스 초기화
    try:
        app.state.tcfd_analysis_service = TCFDAnalysisService()
        app.state.tcfd_report_service = TCFDReportService()
        app.state.risk_assessment_service = RiskAssessmentService()
        
        # AI 서비스 초기화
        ai_initialized = await app.state.tcfd_analysis_service.initialize_ai_services()
        if ai_initialized:
            logger.info("✅ AI 서비스 초기화 완료")
        else:
            logger.warning("⚠️ AI 서비스 초기화 실패 (API 키 없음)")
            
    except Exception as e:
        logger.error(f"❌ AI 서비스 초기화 실패: {str(e)}")
    
    yield
    
    # 리소스 정리
    logger.info("🛑 TCFD Report Service 종료")
    if hasattr(app.state, 'tcfd_analysis_service'):
        await app.state.tcfd_analysis_service.close()

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

# TCFD 도메인 라우터 포함
from app.domain.tcfd.controller.tcfd_controller import router as tcfd_router
app.include_router(tcfd_router)

# 헬스 체크
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "tcfd-report-service",
        "ai_services": "enabled" if hasattr(app.state, 'tcfd_analysis_service') else "disabled",
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
    port = int(os.getenv("SERVICE_PORT", 8006))
    uvicorn.run(app, host="0.0.0.0", port=port)
