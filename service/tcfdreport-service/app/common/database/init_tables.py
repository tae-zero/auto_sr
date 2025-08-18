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
        # 데이터베이스 연결
        conn = await asyncpg.connect(database_url)
        
        # TCFD 입력 데이터 테이블 생성
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS tcfd_inputs (
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
        
        # 인덱스 생성
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
