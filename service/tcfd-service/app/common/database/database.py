from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# 환경변수 로드
if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv("service/tcfd-service/.env")

# DATABASE_URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/tcfd_db")

# URL 디버깅
print(f"Original DATABASE_URL: {DATABASE_URL}")

# 환경별 URL 처리
railway_env = os.getenv("RAILWAY_ENVIRONMENT")
if railway_env in ["true", "production"]:  # "production"도 인식
    # Railway 환경: postgresql:// 스키마 사용 (asyncpg는 URL에서 제거)
    if DATABASE_URL.startswith("postgresql+asyncpg://"):
        DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgresql+asyncpg://"):]
    elif DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
    
    print(f"🚂 Railway 환경 감지 - postgresql:// 스키마 사용")
else:
    # Docker 환경: psycopg2 사용 (동기)
    if DATABASE_URL.startswith("postgresql+asyncpg://"):
        DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgresql+asyncpg://"):]
    elif DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgres://"):]
    
    print(f"🐳 Docker 환경 감지 - psycopg2 사용")

print(f"Final DATABASE_URL: {DATABASE_URL}")

# Base 클래스 정의 (models.py에서 import할 수 있도록)
Base = declarative_base()

# 환경별 엔진 생성
if railway_env in ["true", "production"]:  # "production"도 인식
    # Railway 환경: 비동기 엔진 (asyncpg 사용)
    try:
        import asyncpg
        print(f"✅ asyncpg 패키지 확인됨: {asyncpg.__version__}")
        # asyncpg가 있으면 postgresql+asyncpg:// 스키마 사용
        if not DATABASE_URL.startswith("postgresql+asyncpg://"):
            DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgresql://"):]
            print(f"🔧 Railway 환경: postgresql+asyncpg:// 스키마로 변경")
        
        engine = create_async_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
    except ImportError:
        print("❌ asyncpg 패키지가 설치되지 않음. psycopg2로 대체합니다.")
        # asyncpg가 없으면 postgresql:// 스키마 사용
        if DATABASE_URL.startswith("postgresql+asyncpg://"):
            DATABASE_URL = "postgresql://" + DATABASE_URL[len("postgresql+asyncpg://"):]
        
        from sqlalchemy import create_engine
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )
else:
    # Docker 환경: 동기 엔진 (psycopg2)
    from sqlalchemy import create_engine
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )

# 환경별 세션 팩토리
if railway_env in ["true", "production"]:  # "production"도 인식
    # Railway 환경: 비동기 세션
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
else:
    # Docker 환경: 동기 세션
    from sqlalchemy.orm import sessionmaker, Session
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

# ... existing code ...

# 환경별 의존성 함수
if railway_env in ["true", "production"]:  # "production"도 인식
    # Railway 환경: 비동기 의존성
    async def get_db():
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
else:
    # Docker 환경: 동기 의존성
    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

# ... existing code ...