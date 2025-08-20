from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# 인증 미들웨어 추가
from app.domain.auth.auth_middleware import get_current_user

app = FastAPI(title="Chatbot Service", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Chatbot Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatbot-service"}

@app.get("/chat")
async def chat(current_user: dict = Depends(get_current_user)):
    """챗봇 엔드포인트 (인증 필요)"""
    return {
        "message": "Chat endpoint", 
        "user": current_user.get('email', 'unknown'),
        "status": "authenticated"
    }
