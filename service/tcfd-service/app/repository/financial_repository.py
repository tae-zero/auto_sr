"""
재무정보 리포지토리
- Railway PostgreSQL 데이터베이스 접근
- 재무정보 CRUD 작업
"""
from typing import List, Optional, Dict, Any
import asyncpg
import os
from app.entity.financial_entity import FinancialDataEntity
from app.model.financial_model import FinancialDataCreate, FinancialDataUpdate, FinancialData

class FinancialRepository:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool = None
    
    async def _get_pool(self):
        """데이터베이스 연결 풀 가져오기"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.database_url)
        return self.pool
    
    async def get_financial_data(self, company_id: Optional[str] = None, fiscal_year: Optional[str] = None) -> List[FinancialData]:
        """재무정보 조회"""
        try:
            pool = await self._get_pool()
            
            query = """
                SELECT 
                    f.id,
                    f.company_id,
                    f.fiscal_year,
                    f.revenue,
                    f.total_assets,
                    f.total_liabilities,
                    f.total_equity,
                    f.operating_income,
                    f.net_income,
                    f.created_at,
                    f.updated_at
                FROM financial_status f
                WHERE 1=1
            """
            params = []
            
            if company_id:
                query += " AND f.company_id = $1"
                params.append(company_id)
            
            if fiscal_year:
                query += f" AND f.fiscal_year = ${len(params) + 1}"
                params.append(fiscal_year)
            
            query += " ORDER BY f.fiscal_year DESC, f.created_at DESC"
            
            async with pool.acquire() as conn:
                rows = await conn.fetch(query, *params)
                
                return [FinancialData(
                    id=row['id'],
                    company_id=row['company_id'],
                    fiscal_year=row['fiscal_year'],
                    revenue=row['revenue'],
                    total_assets=row['total_assets'],
                    total_liabilities=row['total_liabilities'],
                    total_equity=row['total_equity'],
                    operating_income=row['operating_income'],
                    net_income=row['net_income'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                ) for row in rows]
                
        except Exception as e:
            raise Exception(f"재무정보 조회 실패: {str(e)}")
    
    async def get_financial_data_by_id(self, financial_id: str) -> Optional[FinancialData]:
        """ID로 재무정보 조회"""
        try:
            pool = await self._get_pool()
            
            query = """
                SELECT 
                    f.id,
                    f.company_id,
                    f.fiscal_year,
                    f.revenue,
                    f.total_assets,
                    f.total_liabilities,
                    f.total_equity,
                    f.operating_income,
                    f.net_income,
                    f.created_at,
                    f.updated_at
                FROM financial_status f
                WHERE f.id = $1
            """
            
            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, financial_id)
                
                if not row:
                    return None
                
                return FinancialData(
                    id=row['id'],
                    company_id=row['company_id'],
                    fiscal_year=row['fiscal_year'],
                    revenue=row['revenue'],
                    total_assets=row['total_assets'],
                    total_liabilities=row['total_liabilities'],
                    total_equity=row['total_equity'],
                    operating_income=row['operating_income'],
                    net_income=row['net_income'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                
        except Exception as e:
            raise Exception(f"재무정보 조회 실패: {str(e)}")
    
    async def create_financial_data(self, data: FinancialDataCreate) -> FinancialData:
        """재무정보 생성"""
        try:
            pool = await self._get_pool()
            
            query = """
                INSERT INTO financial_status (
                    company_id, fiscal_year, revenue, total_assets,
                    total_liabilities, total_equity, operating_income, net_income
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id, created_at, updated_at
            """
            
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    query,
                    data.company_id,
                    data.fiscal_year,
                    data.revenue,
                    data.total_assets,
                    data.total_liabilities,
                    data.total_equity,
                    data.operating_income,
                    data.net_income
                )
                
                return FinancialData(
                    id=row['id'],
                    company_id=data.company_id,
                    fiscal_year=data.fiscal_year,
                    revenue=data.revenue,
                    total_assets=data.total_assets,
                    total_liabilities=data.total_liabilities,
                    total_equity=data.total_equity,
                    operating_income=data.operating_income,
                    net_income=data.net_income,
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                
        except Exception as e:
            raise Exception(f"재무정보 생성 실패: {str(e)}")
    
    async def update_financial_data(self, financial_id: str, data: FinancialDataUpdate) -> Optional[FinancialData]:
        """재무정보 업데이트"""
        try:
            pool = await self._get_pool()
            
            # 업데이트할 필드만 동적으로 구성
            update_fields = []
            params = [financial_id]
            param_count = 1
            
            if data.revenue is not None:
                update_fields.append(f"revenue = ${param_count + 1}")
                params.append(data.revenue)
                param_count += 1
            
            if data.total_assets is not None:
                update_fields.append(f"total_assets = ${param_count + 1}")
                params.append(data.total_assets)
                param_count += 1
            
            if data.total_liabilities is not None:
                update_fields.append(f"total_liabilities = ${param_count + 1}")
                params.append(data.total_liabilities)
                param_count += 1
            
            if data.total_equity is not None:
                update_fields.append(f"total_equity = ${param_count + 1}")
                params.append(data.total_equity)
                param_count += 1
            
            if data.operating_income is not None:
                update_fields.append(f"operating_income = ${param_count + 1}")
                params.append(data.operating_income)
                param_count += 1
            
            if data.net_income is not None:
                update_fields.append(f"net_income = ${param_count + 1}")
                params.append(data.net_income)
                param_count += 1
            
            if not update_fields:
                raise ValueError("업데이트할 필드가 없습니다")
            
            query = f"""
                UPDATE financial_status 
                SET {', '.join(update_fields)}, updated_at = NOW()
                WHERE id = $1
                RETURNING id, company_id, fiscal_year, revenue, total_assets,
                         total_liabilities, total_equity, operating_income, net_income,
                         created_at, updated_at
            """
            
            async with pool.acquire() as conn:
                row = await conn.fetchrow(query, *params)
                
                if not row:
                    return None
                
                return FinancialData(
                    id=row['id'],
                    company_id=row['company_id'],
                    fiscal_year=row['fiscal_year'],
                    revenue=row['revenue'],
                    total_assets=row['total_assets'],
                    total_liabilities=row['total_liabilities'],
                    total_equity=row['total_equity'],
                    operating_income=row['operating_income'],
                    net_income=row['net_income'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                
        except Exception as e:
            raise Exception(f"재무정보 업데이트 실패: {str(e)}")
    
    async def delete_financial_data(self, financial_id: str) -> bool:
        """재무정보 삭제"""
        try:
            pool = await self._get_pool()
            
            query = "DELETE FROM financial_status WHERE id = $1"
            
            async with pool.acquire() as conn:
                result = await conn.execute(query, financial_id)
                return result == "DELETE 1"
                
        except Exception as e:
            raise Exception(f"재무정보 삭제 실패: {str(e)}")
    
    async def close(self):
        """데이터베이스 연결 풀 종료"""
        if self.pool:
            await self.pool.close()
