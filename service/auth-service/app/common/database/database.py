"""
Auth Service Database Configuration
"""
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import text

logger = logging.getLogger("auth_service_db")

# Railway PostgreSQL 연결 설정 (환경변수 우선, 기본값 사용)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.warning("⚠️ DATABASE_URL 환경변수가 설정되지 않았습니다.")
    # Railway에서 기본값 설정
    DATABASE_URL = "postgresql://postgres:YgIQJWEaQShbuQhRsAdVaeBUZatEgrQO@postgres.railway.internal:5432/railway"
    logger.info("ℹ️ 기본 Railway PostgreSQL URL을 사용합니다.")

# Railway PostgreSQL URL을 asyncpg용으로 변환
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

logger.info(f"✅ Railway PostgreSQL 연결 설정 완료: {DATABASE_URL.split('@')[0]}@***")

# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

# 비동기 세션 팩토리
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base 클래스
Base = declarative_base()

# DB 세션 의존성
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# 연결 테스트 함수
async def test_connection():
    """데이터베이스 연결을 테스트합니다."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("✅ 데이터베이스 연결 성공")
        return True
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
        return False

# 테이블 생성 함수 (존재하지 않는 경우에만 생성, 데이터 보호)
async def create_tables():
    try:
        async with engine.begin() as conn:
            # 테이블 존재 여부 확인
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'user'
                );
            """))
            table_exists = result.scalar()

            if not table_exists:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ 데이터베이스 테이블이 생성되었습니다.")
            else:
                # 기존 데이터 개수 확인
                count_result = await conn.execute(text("SELECT COUNT(*) FROM user"))
                user_count = count_result.scalar()
                logger.info(f"ℹ️ 데이터베이스 테이블이 이미 존재합니다. (기존 사용자: {user_count}명)")
    except Exception as e:
        logger.error(f"❌ 테이블 생성 중 오류: {str(e)}")
        raise
