from typing import List, Optional
import asyncpg
from ..entity.tcfd_input_entity import TCFDInputEntity

class TCFDInputRepository:
    """TCFD 입력 데이터 Repository"""
    
    def __init__(self):
        pass
    
    async def save(self, conn: asyncpg.Connection, tcfd_input: TCFDInputEntity) -> int:
        """TCFD 입력 데이터 저장"""
        query = """
        INSERT INTO tcfd_inputs (
            company_name, user_id, governance_g1, governance_g2, strategy_s1, strategy_s2, strategy_s3,
            risk_management_r1, risk_management_r2, risk_management_r3, metrics_targets_m1, metrics_targets_m2, metrics_targets_m3, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW(), NOW())
        RETURNING id
        """
        
        result = await conn.fetchrow(
            query,
            tcfd_input.company_name,
            tcfd_input.user_id,
            tcfd_input.governance_g1,
            tcfd_input.governance_g2,
            tcfd_input.strategy_s1,
            tcfd_input.strategy_s2,
            tcfd_input.strategy_s3,
            tcfd_input.risk_management_r1,
            tcfd_input.risk_management_r2,
            tcfd_input.risk_management_r3,
            tcfd_input.metrics_targets_m1,
            tcfd_input.metrics_targets_m2,
            tcfd_input.metrics_targets_m3
        )
        
        return result['id']
    
    async def find_by_id(self, conn: asyncpg.Connection, input_id: int) -> Optional[TCFDInputEntity]:
        """ID로 TCFD 입력 데이터 조회"""
        query = """
        SELECT id, company_name, user_id, governance_g1, governance_g2, strategy_s1, strategy_s2, strategy_s3,
               risk_management_r1, risk_management_r2, risk_management_r3, metrics_targets_m1, metrics_targets_m2, metrics_targets_m3, created_at, updated_at
        FROM tcfd_inputs WHERE id = $1
        """
        
        result = await conn.fetchrow(query, input_id)
        
        if not result:
            return None
        
        return TCFDInputEntity(
            id=result['id'],
            company_name=result['company_name'],
            user_id=result['user_id'],
            g1_text=result['g1_text'],
            g2_text=result['g2_text'],
            s1_text=result['s1_text'],
            s2_text=result['s2_text'],
            s3_text=result['s3_text'],
            r1_text=result['r1_text'],
            r2_text=result['r2_text'],
            r3_text=result['r3_text'],
            m1_text=result['m1_text'],
            m2_text=result['m2_text'],
            m3_text=result['m3_text'],
            created_at=result['created_at'],
            updated_at=result['updated_at']
        )
    
    async def find_by_company(self, conn: asyncpg.Connection, company_name: str) -> List[TCFDInputEntity]:
        """회사명으로 TCFD 입력 데이터 조회"""
        query = """
        SELECT id, company_name, user_id, g1_text, g2_text, s1_text, s2_text, s3_text,
               r1_text, r2_text, r3_text, m1_text, m2_text, m3_text, created_at, updated_at
        FROM tcfd_inputs WHERE company_name = $1 ORDER BY created_at DESC
        """
        
        results = await conn.fetch(query, company_name)
        
        entities = []
        for result in results:
            entity = TCFDInputEntity(
                id=result['id'],
                company_name=result['company_name'],
                user_id=result['user_id'],
                g1_text=result['g1_text'],
                g2_text=result['g2_text'],
                s1_text=result['s1_text'],
                s2_text=result['s2_text'],
                s3_text=result['s3_text'],
                r1_text=result['r1_text'],
                r2_text=result['r2_text'],
                r3_text=result['r3_text'],
                m1_text=result['m1_text'],
                m2_text=result['m2_text'],
                m3_text=result['m3_text'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
            entities.append(entity)
        
        return entities
    
    async def find_by_user(self, conn: asyncpg.Connection, user_id: str) -> List[TCFDInputEntity]:
        """사용자 ID로 TCFD 입력 데이터 조회"""
        query = """
        SELECT id, company_name, user_id, g1_text, g2_text, s1_text, s2_text, s3_text,
               r1_text, r2_text, r3_text, m1_text, m2_text, m3_text, created_at, updated_at
        FROM tcfd_inputs WHERE user_id = $1 ORDER BY created_at DESC
        """
        
        results = await conn.fetch(query, user_id)
        
        entities = []
        for result in results:
            entity = TCFDInputEntity(
                id=result['id'],
                company_name=result['company_name'],
                user_id=result['user_id'],
                g1_text=result['g1_text'],
                g2_text=result['g2_text'],
                s1_text=result['s1_text'],
                s2_text=result['s2_text'],
                s3_text=result['s3_text'],
                r1_text=result['r1_text'],
                r2_text=result['r2_text'],
                r3_text=result['r3_text'],
                m1_text=result['m1_text'],
                m2_text=result['m2_text'],
                m3_text=result['m3_text'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
            entities.append(entity)
        
        return entities
    
    async def update(self, conn: asyncpg.Connection, input_id: int, tcfd_input: TCFDInputEntity) -> bool:
        """TCFD 입력 데이터 업데이트"""
        query = """
        UPDATE tcfd_inputs SET
            g1_text = $1, g2_text = $2, s1_text = $3, s2_text = $4, s3_text = $5,
            r1_text = $6, r2_text = $7, r3_text = $8, m1_text = $9, m2_text = $10, m3_text = $11,
            updated_at = NOW()
        WHERE id = $12
        """
        
        result = await conn.execute(
            query,
            tcfd_input.g1_text,
            tcfd_input.g2_text,
            tcfd_input.s1_text,
            tcfd_input.s2_text,
            tcfd_input.s3_text,
            tcfd_input.r1_text,
            tcfd_input.r2_text,
            tcfd_input.r3_text,
            tcfd_input.m1_text,
            tcfd_input.m2_text,
            tcfd_input.m3_text,
            input_id
        )
        
        return result != "UPDATE 0"
    
    async def delete(self, conn: asyncpg.Connection, input_id: int) -> bool:
        """TCFD 입력 데이터 삭제"""
        query = "DELETE FROM tcfd_inputs WHERE id = $1"
        result = await conn.execute(query, input_id)
        return result != "DELETE 0"
    
    async def find_all(self, conn: asyncpg.Connection) -> List[TCFDInputEntity]:
        """모든 TCFD 입력 데이터 조회"""
        query = """
        SELECT id, company_name, user_id, g1_text, g2_text, s1_text, s2_text, s3_text,
               r1_text, r2_text, r3_text, m1_text, m2_text, m3_text, created_at, updated_at
        FROM tcfd_inputs ORDER BY created_at DESC
        """
        
        results = await conn.fetch(query)
        
        entities = []
        for result in results:
            entity = TCFDInputEntity(
                id=result['id'],
                company_name=result['company_name'],
                user_id=result['user_id'],
                g1_text=result['g1_text'],
                g2_text=result['g2_text'],
                s1_text=result['s1_text'],
                s2_text=result['s2_text'],
                s3_text=result['s3_text'],
                r1_text=result['r1_text'],
                r2_text=result['r2_text'],
                r3_text=result['r3_text'],
                m1_text=result['m1_text'],
                m2_text=result['m2_text'],
                m3_text=result['m3_text'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
            entities.append(entity)
        
        return entities
