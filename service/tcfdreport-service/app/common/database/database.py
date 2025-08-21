"""
데이터베이스 연결 설정
"""
import os
import asyncpg
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """데이터베이스 연결 관리 클래스"""
    
    def __init__(self):
        """데이터베이스 연결 초기화"""
        self.pool: Optional[asyncpg.Pool] = None
        database_url = os.getenv("DATABASE_URL")
        
        # asyncpg는 postgresql:// 스키마를 기대함
        if database_url.startswith(("postgresql+asyncpg://", "postgres://")):
            database_url = database_url.replace("postgresql+asyncpg://", "postgresql://").replace("postgres://", "postgresql://")
        
        self.database_url = database_url
    
    async def connect(self):
        """데이터베이스 연결 풀 생성"""
        if not self.database_url:
            logger.warning("⚠️ DATABASE_URL이 설정되지 않음")
            return False
            
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=10
            )
            logger.info("✅ 데이터베이스 연결 풀 생성 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            return False
    
    async def disconnect(self):
        """데이터베이스 연결 풀 종료"""
        if self.pool:
            await self.pool.close()
            logger.info("🛑 데이터베이스 연결 풀 종료")
    
    async def get_connection(self):
        """데이터베이스 연결 가져오기"""
        if not self.pool:
            raise Exception("데이터베이스 연결 풀이 초기화되지 않음")
        return await self.pool.acquire()
    
    async def release_connection(self, connection):
        """데이터베이스 연결 반환"""
        if self.pool:
            await self.pool.release(connection)

# 전역 데이터베이스 인스턴스
database = Database()