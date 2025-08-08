"""
Auth 서비스 메인 애플리케이션 진입점
"""
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager

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

# DB 관련 import
from app.common.database.database import get_db, create_tables, test_connection
from app.domain.auth.service.signup_service import SignupService

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Auth Service 시작")

    # Railway PostgreSQL 연결 대기
    import asyncio
    await asyncio.sleep(2)

    # Railway 데이터베이스 연결 테스트
    db_connected = await test_connection()
    if db_connected:
        # 환경변수로 초기화 제어 (기본값: True)
        should_init_db = os.getenv("INIT_DATABASE", "true").lower() == "true"
        if should_init_db:
            # 테이블 생성
            await create_tables()
            logger.info("✅ Railway 데이터베이스 초기화 완료")
        else:
            logger.info("ℹ️ Railway 데이터베이스 초기화가 비활성화되었습니다.")
    else:
        logger.error("❌ Railway 데이터베이스 연결 실패 - 서비스가 시작되지 않습니다")
        raise Exception("Railway PostgreSQL 연결에 실패했습니다")
    
    yield
    logger.info("🛑 Auth Service 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Service",
    version="0.1.0",
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 로컬 접근
        "http://127.0.0.1:3000",  # 로컬 IP 접근
        "http://frontend:3000",   # Docker 내부 네트워크
        "https://www.taezero.com",  # 프로덕션 도메인
        "https://taezero.com",      # 프로덕션 도메인 (www 없이)
    ],
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
async def login_process(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("🔐 로그인 POST 요청 받음")
    try:
        # 요청 본문에서 formData 읽기
        form_data = await request.json()
        logger.info(f"로그인 시도: {form_data.get('auth_id', 'N/A')}")
        
        # TODO: 로그인 로직 구현 (비밀번호 검증 등)
        return {"로그인": "성공", "받은 데이터": form_data}
    except Exception as e:
        logger.error(f"로그인 처리 중 오류: {str(e)}")
        return {"로그인": "실패", "오류": str(e)}

@app.get("/auth/signup")
async def signup():
    return {"message": "Signup endpoint", "status": "success"}

@app.post("/auth/signup")
async def signup_process(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("📝 회원가입 POST 요청 받음")
    try:
        # 요청 본문에서 formData 읽기
        form_data = await request.json()
        
        # 필수 필드 검증
        required_fields = ['company_id', 'industry', 'email', 'name', 'age', 'auth_id', 'auth_pw']
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        
        if missing_fields:
            logger.warning(f"필수 필드 누락: {missing_fields}")
            return {
                "회원가입": "실패",
                "message": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            }
        
        # 새로운 컬럼명에 맞춰 로그 출력
        logger.info("=== 회원가입 요청 데이터 ===")
        logger.info(f"회사 ID: {form_data.get('company_id', 'N/A')}")
        logger.info(f"산업: {form_data.get('industry', 'N/A')}")
        logger.info(f"이메일: {form_data.get('email', 'N/A')}")
        logger.info(f"이름: {form_data.get('name', 'N/A')}")
        logger.info(f"나이: {form_data.get('age', 'N/A')}")
        logger.info(f"인증 ID: {form_data.get('auth_id', 'N/A')}")
        logger.info(f"인증 비밀번호: [PROTECTED]")
        logger.info("==========================")
        
        # PostgreSQL에 사용자 저장
        result = await SignupService.create_user(db, form_data)
        
        if result["success"]:
            logger.info(f"✅ 회원가입 성공: {form_data['email']}")
            return {
                "회원가입": "성공",
                "message": result["message"],
                "user_id": result.get("user_id")
            }
        else:
            logger.warning(f"❌ 회원가입 실패: {result['message']}")
            return {
                "회원가입": "실패",
                "message": result["message"]
            }
            
    except Exception as e:
        logger.error(f"회원가입 처리 중 오류: {str(e)}")
        return {"회원가입": "실패", "오류": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(PORT)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)