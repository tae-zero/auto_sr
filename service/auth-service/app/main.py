"""
Auth 서비스 메인 애플리케이션 진입점
"""
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware

# SQLAlchemy AsyncSession 강제 import
try:
    from sqlalchemy.ext.asyncio import AsyncSession
    print("✅ AsyncSession import 성공")
except ImportError as e:
    print(f"❌ AsyncSession import 실패: {e}")
    # 대체 방법
    import sqlalchemy.ext.asyncio
    AsyncSession = sqlalchemy.ext.asyncio.AsyncSession
    print("✅ AsyncSession 대체 import 성공")

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
from app.domain.auth.service.login_service import LoginService

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Auth Service 시작")

    # Railway PostgreSQL 연결 대기 (시간 단축)
    import asyncio
    await asyncio.sleep(1)

    # Railway 데이터베이스 연결 테스트
    try:
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
            logger.warning("⚠️ Railway 데이터베이스 연결 실패 - 서비스는 계속 실행됩니다")
    except Exception as e:
        logger.warning(f"⚠️ 데이터베이스 초기화 중 오류 (서비스는 계속 실행): {str(e)}")
    
    # 서비스 시작 완료 로그
    logger.info("✅ Auth Service 시작 완료 - Health endpoint 사용 가능")
    
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
        "http://localhost:3001",  # 로컬 접근 (포트 3001)
        "http://127.0.0.1:3000",  # 로컬 IP 접근
        "http://127.0.0.1:3001",  # 로컬 IP 접근 (포트 3001)
        "http://frontend:3000",   # Docker 내부 네트워크
        "https://www.taezero.com",  # 프로덕션 도메인
        "https://taezero.com",      # 프로덕션 도메인 (www 없이)
        "https://auth-service-production-1deb.up.railway.app",  # Railway auth-service
        "*"  # 개발 환경에서 모든 origin 허용
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Auth Service", "version": "0.1.0"}

@app.get("/test")
async def test():
    return {"message": "Auth Service Test Endpoint", "status": "success"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}

@app.get("/login")
async def login():
    return {"message": "Login endpoint", "status": "success"}

@app.post("/login")
async def login_process(request: Request, db=Depends(get_db)):
    # 함수 내에서 AsyncSession 타입 힌트 재정의
    from sqlalchemy.ext.asyncio import AsyncSession
    db: AsyncSession = db
    logger.info("🔐 로그인 POST 요청 받음")
    try:
        # 요청 본문에서 formData 읽기
        form_data = await request.json()
        logger.info(f"로그인 시도: {form_data.get('auth_id', 'N/A')}")
        
        # 필수 필드 검증
        required_fields = ['auth_id', 'auth_pw']
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        
        if missing_fields:
            logger.warning(f"필수 필드 누락: {missing_fields}")
            return {
                "success": False,
                "message": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            }
        
        # LoginService를 통한 인증
        result = await LoginService.authenticate_user(
            db, 
            form_data['auth_id'], 
            form_data['auth_pw']
        )
        
        return result
        
    except Exception as e:
        logger.error(f"로그인 처리 중 오류: {str(e)}")
        return {"success": False, "message": f"로그인 처리 중 오류가 발생했습니다: {str(e)}"}

@app.get("/signup")
async def signup():
    return {"message": "Signup endpoint", "status": "success"}

@app.post("/signup")
async def signup_process(request: Request, db=Depends(get_db)):
    # 함수 내에서 AsyncSession 타입 힌트 재정의
    from sqlalchemy.ext.asyncio import AsyncSession
    db: AsyncSession = db
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
                "success": True,
                "message": result["message"],
                "user_id": result.get("user_id"),
                "email": result.get("email")
            }
        else:
            logger.warning(f"❌ 회원가입 실패: {result['message']}")
            return {
                "success": False,
                "message": result["message"]
            }
            
    except Exception as e:
        logger.error(f"회원가입 처리 중 오류: {str(e)}")
        return {"회원가입": "실패", "오류": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(PORT)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)