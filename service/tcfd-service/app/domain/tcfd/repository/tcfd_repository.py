"""
TCFD Service TCFD 리포지토리
- TCFD 데이터 접근 및 관리
- 6개 테이블 (직원, 손익계산, 임원, 재무상태, 기업, 전체기업) 통합 관리
- AI 분석 결과, 위험 평가, 보고서 저장
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncpg
import os

from app.domain.tcfd.entity.tcfd_entity import TCFDEntity, ClimateRiskEntity

logger = logging.getLogger(__name__)

class TCFDRepository:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'railway')
        }
        self.pool = None
    
    async def get_connection(self):
        """데이터베이스 연결 풀에서 연결 가져오기"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(**self.db_config)
        return await self.pool.acquire()
    
    async def get_all_financial_data(self) -> Dict[str, Any]:
        """6개 테이블의 모든 재무 데이터 조회"""
        try:
            conn = await self.get_connection()
            
            # 6개 테이블 데이터 조회
            data = {}
            
            # 1. 직원 테이블
            employee_query = "SELECT * FROM employee LIMIT 100"
            employee_data = await conn.fetch(employee_query)
            data['employee'] = [dict(row) for row in employee_data]
            
            # 2. 손익계산 테이블
            profit_loss_query = "SELECT * FROM profit_loss LIMIT 100"
            profit_loss_data = await conn.fetch(profit_loss_query)
            data['profit_loss'] = [dict(row) for row in profit_loss_data]
            
            # 3. 임원 테이블
            executive_query = "SELECT * FROM executive LIMIT 100"
            executive_data = await conn.fetch(executive_query)
            data['executive'] = [dict(row) for row in executive_data]
            
            # 4. 재무상태 테이블
            financial_status_query = "SELECT * FROM financial_status LIMIT 100"
            financial_status_data = await conn.fetch(financial_status_query)
            data['financial_status'] = [dict(row) for row in financial_status_data]
            
            # 5. 기업 테이블
            corp_query = "SELECT * FROM corp LIMIT 100"
            corp_data = await conn.fetch(corp_query)
            data['corp'] = [dict(row) for row in corp_data]
            
            # 6. 전체기업 테이블
            all_corp_query = "SELECT * FROM all_corp LIMIT 100"
            all_corp_data = await conn.fetch(all_corp_query)
            data['all_corp'] = [dict(row) for row in all_corp_data]
            
            await self.pool.release(conn)
            
            return {
                "total_records": sum(len(v) for v in data.values()),
                "tables": list(data.keys()),
                "data": data
            }
            
        except Exception as e:
            logger.error(f"재무 데이터 조회 실패: {str(e)}")
            raise Exception(f"재무 데이터 조회 실패: {str(e)}")
    
    async def create_financial_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """재무 데이터 생성 (테이블별로 분기)"""
        try:
            conn = await self.get_connection()
            
            table_name = data.get('table_name')
            if not table_name:
                raise Exception("테이블명이 지정되지 않았습니다")
            
            # 테이블별 데이터 삽입
            if table_name == 'employee':
                result = await self._insert_employee(conn, data)
            elif table_name == 'profit_loss':
                result = await self._insert_profit_loss(conn, data)
            elif table_name == 'executive':
                result = await self._insert_executive(conn, data)
            elif table_name == 'financial_status':
                result = await self._insert_financial_status(conn, data)
            elif table_name == 'corp':
                result = await self._insert_corp(conn, data)
            elif table_name == 'all_corp':
                result = await self._insert_all_corp(conn, data)
            else:
                raise Exception(f"지원하지 않는 테이블: {table_name}")
            
            await self.pool.release(conn)
            return result
            
        except Exception as e:
            logger.error(f"재무 데이터 생성 실패: {str(e)}")
            raise Exception(f"재무 데이터 생성 실패: {str(e)}")
    
    async def save_analysis_result(self, entity: TCFDEntity) -> bool:
        """AI 분석 결과 저장"""
        try:
            conn = await self.get_connection()
            
            query = """
                INSERT INTO tcfd_analysis_results 
                (company_info, analysis_result, status, created_at) 
                VALUES ($1, $2, $3, $4)
            """
            
            await conn.execute(
                query,
                str(entity.company_info),
                str(entity.analysis_result),
                entity.status,
                datetime.utcnow()
            )
            
            await self.pool.release(conn)
            return True
            
        except Exception as e:
            logger.error(f"분석 결과 저장 실패: {str(e)}")
            raise Exception(f"분석 결과 저장 실패: {str(e)}")
    
    async def save_risk_assessment(self, entity: ClimateRiskEntity) -> bool:
        """위험 평가 결과 저장"""
        try:
            conn = await self.get_connection()
            
            query = """
                INSERT INTO tcfd_risk_assessments 
                (company_info, financial_data, risk_assessment, status, created_at) 
                VALUES ($1, $2, $3, $4, $5)
            """
            
            await conn.execute(
                query,
                str(entity.company_info),
                str(entity.financial_data),
                str(entity.risk_assessment),
                entity.status,
                datetime.utcnow()
            )
            
            await self.pool.release(conn)
            return True
            
        except Exception as e:
            logger.error(f"위험 평가 결과 저장 실패: {str(e)}")
            raise Exception(f"위험 평가 결과 저장 실패: {str(e)}")
    
    async def save_report_result(self, entity: TCFDEntity) -> bool:
        """보고서 생성 결과 저장"""
        try:
            conn = await self.get_connection()
            
            query = """
                INSERT INTO tcfd_reports 
                (company_info, financial_data, risk_assessment, report_result, status, created_at) 
                VALUES ($1, $2, $3, $4, $5, $6)
            """
            
            await conn.execute(
                query,
                str(entity.company_info),
                str(entity.financial_data),
                str(entity.risk_assessment),
                str(entity.report_result),
                entity.status,
                datetime.utcnow()
            )
            
            await self.pool.release(conn)
            return True
            
        except Exception as e:
            logger.error(f"보고서 결과 저장 실패: {str(e)}")
            raise Exception(f"보고서 결과 저장 실패: {str(e)}")
    
    async def get_climate_scenarios(self) -> Dict[str, Any]:
        """기후 시나리오 데이터 조회"""
        try:
            conn = await self.get_connection()
            
            query = "SELECT * FROM climate_scenarios ORDER BY scenario_id"
            scenarios = await conn.fetch(query)
            
            await self.pool.release(conn)
            
            return {
                "scenarios": [dict(row) for row in scenarios],
                "total_count": len(scenarios)
            }
            
        except Exception as e:
            logger.error(f"기후 시나리오 조회 실패: {str(e)}")
            raise Exception(f"기후 시나리오 조회 실패: {str(e)}")
    
    # 테이블별 삽입 메서드들
    async def _insert_employee(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """직원 데이터 삽입"""
        query = """
            INSERT INTO employee (id, name, position, department, salary, hire_date)
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('name'),
            data.get('position'),
            data.get('department'),
            data.get('salary'),
            data.get('hire_date')
        )
        return {"message": "직원 데이터 생성 완료", "table": "employee"}
    
    async def _insert_profit_loss(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """손익계산 데이터 삽입"""
        query = """
            INSERT INTO profit_loss (id, revenue, expenses, net_income, period)
            VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('revenue'),
            data.get('expenses'),
            data.get('net_income'),
            data.get('period')
        )
        return {"message": "손익계산 데이터 생성 완료", "table": "profit_loss"}
    
    async def _insert_executive(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """임원 데이터 삽입"""
        query = """
            INSERT INTO executive (id, name, position, compensation, stock_options)
            VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('name'),
            data.get('position'),
            data.get('compensation'),
            data.get('stock_options')
        )
        return {"message": "임원 데이터 생성 완료", "table": "executive"}
    
    async def _insert_financial_status(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """재무상태 데이터 삽입"""
        query = """
            INSERT INTO financial_status (id, assets, liabilities, equity, date)
            VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('assets'),
            data.get('liabilities'),
            data.get('equity'),
            data.get('date')
        )
        return {"message": "재무상태 데이터 생성 완료", "table": "financial_status"}
    
    async def _insert_corp(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """기업 데이터 삽입"""
        query = """
            INSERT INTO corp (id, name, industry, size, location)
            VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('name'),
            data.get('industry'),
            data.get('size'),
            data.get('location')
        )
        return {"message": "기업 데이터 생성 완료", "table": "corp"}
    
    async def _insert_all_corp(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """전체기업 데이터 삽입"""
        query = """
            INSERT INTO all_corp (id, name, sector, market_cap, employees)
            VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('name'),
            data.get('sector'),
            data.get('market_cap'),
            data.get('employees')
        )
        return {"message": "전체기업 데이터 생성 완료", "table": "all_corp"}
    
    async def close(self):
        """리소스 정리"""
        if self.pool:
            await self.pool.close()
