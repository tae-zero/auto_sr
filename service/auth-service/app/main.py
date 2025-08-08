from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sys
from dotenv import load_dotenv

# 환경 변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

# Railway 환경변수 처리
PORT = os.getenv("PORT", "8008")
if not PORT.isdigit():
    PORT = "8008"

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("auth_service")

# FastAPI 앱 생성
app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Service",
    version="0.1.0"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Auth Service", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}

@app.get("/auth/login")
async def login():
    return {"message": "Login endpoint", "status": "success"}

@app.post("/auth/login")
async def login_process():
    return {"message": "Login process", "status": "success"}

@app.get("/auth/signup")
async def signup():
    return {"message": "Signup endpoint", "status": "success"}

@app.post("/auth/signup")
async def signup_process():
    return {"message": "Signup process", "status": "success"}

if __name__ == "__main__":
    import uvicorn
    port = int(PORT)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
