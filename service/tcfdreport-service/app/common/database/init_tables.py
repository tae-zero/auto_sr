"""
데이터베이스 테이블 자동 생성 스크립트
"""
import asyncpg
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def init_tables(database_url: str):
    """데이터베이스 테이블 초기화"""
    try:
        # URL 스키마 수정
        if database_url.startswith("postgresql+asyncpg://"):
            database_url = "postgresql://" + database_url[len("postgresql+asyncpg://"):]
        elif database_url.startswith("postgres://"):
            database_url = "postgresql://" + database_url[len("postgres://"):]
            
        # 데이터베이스 연결
        conn = await asyncpg.connect(database_url)
        
        # 테이블이 존재하는지 확인
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'tcfd_inputs'
            );
        """)
        
        if not table_exists:
            # 테이블이 없을 때만 생성
            await conn.execute("""
                CREATE TABLE tcfd_inputs (
                    id SERIAL PRIMARY KEY,
                    company_name VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255),
                    governance_g1 TEXT,
                    governance_g2 TEXT,
                    strategy_s1 TEXT,
                    strategy_s2 TEXT,
                    strategy_s3 TEXT,
                    risk_management_r1 TEXT,
                    risk_management_r2 TEXT,
                    risk_management_r3 TEXT,
                    metrics_targets_m1 TEXT,
                    metrics_targets_m2 TEXT,
                    metrics_targets_m3 TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("✅ tcfd_inputs 테이블 생성 완료")
        else:
            # 테이블이 존재하면 데이터만 삭제 (테이블 구조는 유지)
            # await conn.execute("DELETE FROM tcfd_inputs;")
            # 시퀀스도 초기화 (id를 1부터 다시 시작)
            # await conn.execute("ALTER SEQUENCE tcfd_inputs_id_seq RESTART WITH 1;")
            logger.info("✅ 기존 tcfd_inputs 테이블 데이터 완료")
        
        # 인덱스가 없으면 생성
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_company_name ON tcfd_inputs(company_name);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_user_id ON tcfd_inputs(user_id);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_created_at ON tcfd_inputs(created_at);
        """)
        
        await conn.close()
        logger.info("✅ 데이터베이스 테이블 초기화 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 테이블 초기화 실패: {str(e)}")
        return False
