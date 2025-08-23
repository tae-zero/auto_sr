from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv

# 환경변수 로드
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

# 인증 미들웨어 추가
from app.domain.auth.auth_middleware import get_current_user

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=os.getenv("SERVICE_NAME", "Chatbot Service"), 
    version="1.0.0",
    description="AI 챗봇 서비스 - MSV Pattern with Layered Architecture"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 초기화 작업"""
    try:
        logger.info("🚀 Chatbot Service 시작")
        logger.info("✅ Chatbot Service 초기화 완료")
    except Exception as e:
        logger.error(f"❌ Chatbot Service 초기화 실패: {e}")
        logger.info("⚠️ 서비스는 계속 실행됩니다")

@app.get("/")
async def root():
    return {
        "message": "Chatbot Service is running",
        "version": "1.0.0",
        "architecture": "MSV Pattern with Layered Architecture"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "chatbot-service",
        "architecture": "MSV Pattern with Layered Architecture"
    }

@app.get("/chat")
async def chat(current_user: dict = Depends(get_current_user)):
    """챗봇 엔드포인트 (인증 필요)"""
    try:
        return {
            "message": "Chat endpoint", 
            "user": current_user.get('email', 'unknown'),
            "status": "authenticated",
            "service": "chatbot-service"
        }
    except Exception as e:
        logger.error(f"챗봇 엔드포인트 오류: {e}")
        raise HTTPException(status_code=500, detail="챗봇 서비스 오류")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", os.getenv("PORT", "8001")))
    uvicorn.run(app, host=os.getenv("SERVICE_HOST", "0.0.0.0"), port=port)
