import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

# Railway PostgreSQL 연결 설정
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Railway PostgreSQL URL을 asyncpg용으로 변환
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://") and "asyncpg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    logger.info(f"데이터베이스 연결 설정 완료: {DATABASE_URL.split('@')[0]}@***")
else:
    # 로컬 개발용 기본값 (Docker 환경)
    DATABASE_URL = "postgresql+asyncpg://postgres:password@postgres:5432/esg_mate"
    logger.warning("DATABASE_URL이 없습니다. Docker PostgreSQL 사용")

# 비동기 엔진 생성 (asyncpg 전용)
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL 로그 출력 (개발용)
    future=True,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=300,  # 5분마다 연결 재생성
    pool_size=10,  # 연결 풀 크기
    max_overflow=20  # 최대 추가 연결 수
)

# 비동기 세션 팩토리
async_session = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base 모델
Base = declarative_base()

# 데이터베이스 세션 의존성
async def get_db():
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"데이터베이스 세션 오류: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

# 테이블 생성 함수 (존재하지 않는 경우에만 생성)
async def create_tables():
    try:
        async with engine.begin() as conn:
            # 테이블 존재 여부 확인
            from sqlalchemy import text
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ 데이터베이스 테이블이 생성되었습니다.")
            else:
                logger.info("ℹ️ 데이터베이스 테이블이 이미 존재합니다.")
    except Exception as e:
        logger.error(f"❌ 테이블 생성 중 오류: {str(e)}")
        raise

# 데이터베이스 연결 테스트 (재시도 로직 포함)
async def test_connection(max_retries=5, delay=2):
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                from sqlalchemy import text
                await conn.execute(text("SELECT 1"))
            logger.info("✅ 데이터베이스 연결 성공!")
            return True
        except Exception as e:
            logger.warning(f"❌ 데이터베이스 연결 시도 {attempt + 1}/{max_retries} 실패: {str(e)}")
            if attempt < max_retries - 1:
                import asyncio
                await asyncio.sleep(delay)
                logger.info(f"🔄 {delay}초 후 재시도...")
            else:
                logger.error(f"❌ 최대 재시도 횟수 초과. 데이터베이스 연결 실패")
                return False