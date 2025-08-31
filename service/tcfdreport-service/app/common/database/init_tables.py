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
        conn = await asyncpg.connect(database_url)
        logger.info("✅ 데이터베이스 연결 성공")
        
        # 1. tcfd_inputs 테이블 확인 및 생성 (기존 로직 보존)
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
        
        # 2. 새로운 tcfd_drafts 테이블 생성
        drafts_table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'tcfd_drafts'
            );
        """)
        
        if not drafts_table_exists:
            await conn.execute("""
                CREATE TABLE tcfd_drafts (
                    id SERIAL PRIMARY KEY,
                    tcfd_input_id INTEGER REFERENCES tcfd_inputs(id),
                    company_name VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255),
                    draft_content TEXT,
                    draft_type VARCHAR(50),
                    file_path VARCHAR(500),
                    status VARCHAR(50) DEFAULT 'processing',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            logger.info("✅ tcfd_drafts 테이블 생성 완료")
        else:
            logger.info("✅ 기존 tcfd_drafts 테이블 확인 완료")
        
        # 3. 기존 인덱스 생성 (기존 로직 보존)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_company_name ON tcfd_inputs(company_name);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_user_id ON tcfd_inputs(user_id);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_created_at ON tcfd_inputs(created_at);
        """)
        
        # 4. 새로운 테이블 인덱스 생성
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_drafts_company_name ON tcfd_drafts(company_name);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_drafts_user_id ON tcfd_drafts(user_id);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_drafts_tcfd_input_id ON tcfd_drafts(tcfd_input_id);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tcfd_drafts_status ON tcfd_drafts(status);
        """)
        
        await conn.close()
        logger.info("✅ 데이터베이스 테이블 초기화 완료")
        
    except Exception as e:
        logger.error(f"❌ 데이터베이스 테이블 초기화 실패: {str(e)}")
        raise
