import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, DateTime, Integer
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Railway PostgreSQL 연결 설정
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Railway PostgreSQL URL 변환 (postgres:// -> postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    logger.info(f"데이터베이스 연결: {DATABASE_URL.split('@')[0]}@***")
else:
    # 로컬 개발용 기본값
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/esg_mate"
    logger.warning("DATABASE_URL이 없습니다. 로컬 개발용 DB 사용")

# 비동기 엔진 생성
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # SQL 로그 출력 (개발용)
    future=True,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=300  # 5분마다 연결 재생성
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

# 테이블 생성 함수
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("데이터베이스 테이블이 생성되었습니다.")

# 데이터베이스 연결 테스트
async def test_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ 데이터베이스 연결 성공!")
        return True
    except Exception as e:
        logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
        return False