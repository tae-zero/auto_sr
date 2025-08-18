"""
TCFD 입력 데이터 서비스
"""
from typing import List, Optional
import logging
from app.domain.tcfd.schema.tcfd_input_schema import (
    TCFDInputCreateSchema,
    TCFDInputResponseSchema
)
from app.domain.tcfd.repository.tcfd_input_repository import TCFDInputRepository
from app.domain.tcfd.entity.tcfd_input_entity import TCFDInputEntity
from app.common.database.database import database

logger = logging.getLogger(__name__)

class TCFDInputService:
    """TCFD 입력 데이터 서비스"""
    
    def __init__(self):
        self.repository = TCFDInputRepository()
    
    async def create_input(self, data: TCFDInputCreateSchema) -> TCFDInputResponseSchema:
        """TCFD 입력 데이터 생성"""
        try:
            # Entity 생성
            entity = TCFDInputEntity(
                company_name=data.company_name,
                user_id=data.user_id,
                governance_g1=data.governance_g1,
                governance_g2=data.governance_g2,
                strategy_s1=data.strategy_s1,
                strategy_s2=data.strategy_s2,
                strategy_s3=data.strategy_s3,
                risk_management_r1=data.risk_management_r1,
                risk_management_r2=data.risk_management_r2,
                risk_management_r3=data.risk_management_r3,
                metrics_targets_m1=data.metrics_targets_m1,
                metrics_targets_m2=data.metrics_targets_m2,
                metrics_targets_m3=data.metrics_targets_m3
            )
            
            # 데이터베이스에 저장
            conn = await database.get_connection()
            try:
                result = await self.repository.save(conn, entity)
                return TCFDInputResponseSchema.from_entity(result)
            finally:
                await database.release_connection(conn)
                
        except Exception as e:
            logger.error(f"TCFD 입력 데이터 생성 실패: {str(e)}")
            raise
    
    async def get_input_by_id(self, input_id: int) -> Optional[TCFDInputResponseSchema]:
        """ID로 TCFD 입력 데이터 조회"""
        try:
            conn = await database.get_connection()
            try:
                entity = await self.repository.find_by_id(conn, input_id)
                if entity:
                    return TCFDInputResponseSchema.from_entity(entity)
                return None
            finally:
                await database.release_connection(conn)
        except Exception as e:
            logger.error(f"TCFD 입력 데이터 조회 실패: {str(e)}")
            raise
    
    async def get_inputs_by_company(self, company_name: str) -> List[TCFDInputResponseSchema]:
        """회사명으로 TCFD 입력 데이터 조회"""
        try:
            conn = await database.get_connection()
            try:
                entities = await self.repository.find_by_company(conn, company_name)
                return [TCFDInputResponseSchema.from_entity(entity) for entity in entities]
            finally:
                await database.release_connection(conn)
        except Exception as e:
            logger.error(f"회사별 TCFD 입력 데이터 조회 실패: {str(e)}")
            raise
    
    async def get_inputs_by_user(self, user_id: str) -> List[TCFDInputResponseSchema]:
        """사용자 ID로 TCFD 입력 데이터 조회"""
        try:
            conn = await database.get_connection()
            try:
                entities = await self.repository.find_by_user(conn, user_id)
                return [TCFDInputResponseSchema.from_entity(entity) for entity in entities]
            finally:
                await database.release_connection(conn)
        except Exception as e:
            logger.error(f"사용자별 TCFD 입력 데이터 조회 실패: {str(e)}")
            raise
    
    async def get_all_inputs(self) -> List[TCFDInputResponseSchema]:
        """모든 TCFD 입력 데이터 조회"""
        try:
            conn = await database.get_connection()
            try:
                entities = await self.repository.find_all(conn)
                return [TCFDInputResponseSchema.from_entity(entity) for entity in entities]
            finally:
                await database.release_connection(conn)
        except Exception as e:
            logger.error(f"전체 TCFD 입력 데이터 조회 실패: {str(e)}")
            raise
