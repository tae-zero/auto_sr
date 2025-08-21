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

# URL이 올바른 형식인지 확인하고 수정
if not DATABASE_URL.startswith(("postgresql://", "postgresql+asyncpg://")):
    # URL이 잘못된 형식으로 들어온 경우 (postgres://로 시작하거나 스키마가 누락된 경우)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL[len("postgres://"):]
    else:
        DATABASE_URL = "postgresql+asyncpg://" + DATABASE_URL

print(f"Final DATABASE_URL: {DATABASE_URL}")

# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base 클래스
Base = declarative_base()

# 비동기 의존성 함수
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()