"""
TCFD Service - Climate-related Financial Disclosures with AI Analysis
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

# TCFD 관련 import
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
    description="Climate-related Financial Disclosures with AI Analysis",
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

# Health Check
@app.get("/health")
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "tcfd-service",
        "ai_services": "enabled" if hasattr(app.state, 'tcfd_analysis_service') else "disabled"
    }

# TCFD 분석 엔드포인트
@app.post("/api/v1/tcfd/analyze-report")
async def analyze_tcfd_report(
    file: UploadFile = File(...),
    company_info: Optional[str] = Form("{}")
):
    """TCFD 보고서 AI 분석"""
    try:
        company_data = json.loads(company_info) if company_info else {}
        
        result = await app.state.tcfd_analysis_service.analyze_report(
            file=file,
            company_info=company_data
        )
        
        return {
            "success": True,
            "analysis_result": result,
            "message": "TCFD 보고서 분석이 완료되었습니다."
        }
        
    except Exception as e:
        logger.error(f"TCFD 보고서 분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 실패: {str(e)}")

@app.post("/api/v1/tcfd/assess-risks")
async def assess_climate_risks(
    company_data: Dict[str, Any]
):
    """기후 리스크 평가"""
    try:
        risk_assessment = await app.state.risk_assessment_service.assess_risks(
            company_data=company_data
        )
        
        return {
            "success": True,
            "risk_assessment": risk_assessment,
            "message": "기후 리스크 평가가 완료되었습니다."
        }
        
    except Exception as e:
        logger.error(f"기후 리스크 평가 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"리스크 평가 실패: {str(e)}")

@app.get("/api/v1/tcfd/generate-report")
async def generate_tcfd_report(
    company_id: str,
    report_type: str = "annual"
):
    """TCFD 보고서 생성"""
    try:
        report = await app.state.tcfd_report_service.generate_report(
            company_id=company_id,
            report_type=report_type
        )
        
        return {
            "success": True,
            "report": report,
            "message": "TCFD 보고서가 생성되었습니다."
        }
        
    except Exception as e:
        logger.error(f"TCFD 보고서 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"보고서 생성 실패: {str(e)}")

@app.post("/api/v1/tcfd/upload-documents")
async def upload_tcfd_documents(
    files: List[UploadFile] = File(...),
    company_id: str = Form(...),
    document_type: str = Form(...)
):
    """TCFD 관련 문서 업로드"""
    try:
        uploaded_docs = []
        
        for file in files:
            doc_info = await app.state.tcfd_analysis_service.upload_document(
                file=file,
                company_id=company_id,
                document_type=document_type
            )
            uploaded_docs.append(doc_info)
        
        return {
            "success": True,
            "uploaded_documents": uploaded_docs,
            "message": f"{len(uploaded_docs)}개의 문서가 업로드되었습니다."
        }
        
    except Exception as e:
        logger.error(f"문서 업로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"문서 업로드 실패: {str(e)}")

@app.get("/api/v1/tcfd/search-knowledge")
async def search_tcfd_knowledge(
    query: str,
    company_id: Optional[str] = None,
    top_k: int = 5
):
    """TCFD 지식 베이스 검색"""
    try:
        search_results = await app.state.tcfd_analysis_service.search_knowledge(
            query=query,
            company_id=company_id,
            top_k=top_k
        )
        
        return {
            "success": True,
            "query": query,
            "results": search_results,
            "total_results": len(search_results)
        }
        
    except Exception as e:
        logger.error(f"지식 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")

# 서비스 정보
@app.get("/api/v1/tcfd/service-info")
async def get_service_info():
    """TCFD 서비스 정보"""
    return {
        "service_name": "TCFD Service",
        "version": "0.1.0",
        "description": "Climate-related Financial Disclosures with AI Analysis",
        "features": [
            "TCFD 보고서 AI 분석",
            "기후 리스크 평가",
            "TCFD 보고서 생성",
            "문서 업로드 및 벡터화",
            "지식 베이스 검색"
        ],
        "ai_capabilities": [
            "LangChain 기반 문서 분석",
            "OpenAI GPT 모델 통합",
            "벡터 데이터베이스 검색",
            "자연어 처리"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8005"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
