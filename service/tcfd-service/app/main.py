"""
TCFD Service - Climate-related Financial Disclosures with AI Analysis
MSV 패턴의 계층형 아키텍처 적용
"""
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Optional, Any
import json

# 환경 변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("tcfd_service")

# 기존 TCFD 서비스들 import (점진적 마이그레이션을 위해 유지)
from app.domain.tcfd.analysis_service import TCFDAnalysisService
from app.domain.tcfd.report_service import TCFDReportService
from app.domain.tcfd.risk_assessment_service import RiskAssessmentService

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 TCFD Service 시작")
    
    # AI 서비스 초기화
    try:
        await app.state.tcfd_analysis_service.initialize_ai_services()
        logger.info("✅ TCFD AI 서비스 초기화 완료")
    except Exception as e:
        logger.warning(f"⚠️ TCFD AI 서비스 초기화 실패 (서비스는 계속 실행): {str(e)}")
    
    yield
    logger.info("🛑 TCFD Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="TCFD Service",
    description="Climate-related Financial Disclosures with AI Analysis - MSV Pattern with Layered Architecture",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://www.taezero.com",
        "https://taezero.com",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# 서비스 초기화
@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 초기화"""
    app.state.tcfd_analysis_service = TCFDAnalysisService()
    app.state.tcfd_report_service = TCFDReportService()
    app.state.risk_assessment_service = RiskAssessmentService()

# ✅ MSV 패턴의 TCFD 도메인 컨트롤러 사용
from app.domain.tcfd.controller.tcfd_controller import router as tcfd_router
app.include_router(tcfd_router)

# Health Check
@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "tcfd-service",
        "architecture": "MSV Pattern with Layered Architecture",
        "ai_services": "enabled" if hasattr(app.state, 'tcfd_analysis_service') else "disabled",
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
        "description": "기후 관련 재무 공시 및 AI 분석 서비스"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
