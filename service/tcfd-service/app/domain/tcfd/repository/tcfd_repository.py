"""
TCFD Service TCFD 리포지토리
- TCFD 데이터 접근 및 관리
- 5개 테이블 (직원, 손익계산, 임원, 재무상태, 전체기업) 통합 관리
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
        # DATABASE_URL 우선, 없으면 개별 환경변수 사용
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # DATABASE_URL 파싱: postgresql://user:password@host:port/database
            try:
                from urllib.parse import urlparse
                parsed = urlparse(database_url)
                self.db_config = {
                    'host': parsed.hostname,
                    'port': parsed.port or 5432,
                    'user': parsed.username,
                    'password': parsed.password,
                    'database': parsed.path.lstrip('/')
                }
                logger.info(f"✅ DATABASE_URL에서 설정 로드: {parsed.hostname}:{parsed.port}")
            except Exception as e:
                logger.error(f"❌ DATABASE_URL 파싱 실패: {str(e)}")
                # 폴백: 개별 환경변수 사용
                self.db_config = {
                    'host': os.getenv('DB_HOST', 'localhost'),
                    'port': os.getenv('DB_PORT', '5432'),
                    'user': os.getenv('DB_USER', 'postgres'),
                    'password': os.getenv('DB_PASSWORD', ''),
                    'database': os.getenv('DB_NAME', 'railway')
                }
        else:
            # 개별 환경변수 사용
            self.db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'railway')
            }
            logger.info(f"✅ 개별 환경변수에서 설정 로드: {self.db_config['host']}:{self.db_config['port']}")
        
        self.pool = None
    
    async def get_connection(self):
        """데이터베이스 연결 풀에서 연결 가져오기"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(**self.db_config)
        return await self.pool.acquire()
    
    async def get_company_financial_data(self, company_name: str) -> Dict[str, Any]:
        """특정 회사의 재무정보 조회 (5개 테이블 통합)"""
        try:
            conn = await self.get_connection()
            
            # 1단계: companyname으로 회사 ID 찾기 (어느 테이블에서든)
            company_id = None
            
            # 각 테이블에서 companyname으로 검색하여 id 찾기
            tables_to_search = ['employee', 'profit_loss', 'executives', 'financial_status', 'all_corporations']
            
            for table in tables_to_search:
                try:
                    # companyname 컬럼이 있는지 확인하고 검색
                    check_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'companyname'"
                    has_companyname = await conn.fetch(check_query)
                    
                    if has_companyname:
                        search_query = f"SELECT id, companyname FROM {table} WHERE companyname ILIKE $1 LIMIT 1"
                        result = await conn.fetch(search_query, f"%{company_name}%")
                        
                        if result:
                            company_id = result[0]['id']
                            found_table = table
                            break
                except Exception as e:
                    logger.warning(f"테이블 {table}에서 companyname 검색 실패: {str(e)}")
                    continue
            
            if not company_id:
                await self.pool.release(conn)
                return {
                    "company_name": company_name,
                    "message": "해당 회사를 찾을 수 없습니다",
                    "data": {}
                }
            
            # 2단계: 찾은 company_id로 5개 테이블에서 모든 데이터 조회
            data = {}
            
            # 각 테이블에서 company_id와 일치하는 데이터 조회
            for table in tables_to_search:
                try:
                    # company_id 컬럼이 있는지 확인
                    check_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'company_id'"
                    has_company_id = await conn.fetch(check_query)
                    
                    if has_company_id:
                        # company_id 컬럼이 있는 경우
                        query = f"SELECT * FROM {table} WHERE company_id = $1"
                        table_data = await conn.fetch(query, company_id)
                    else:
                        # company_id 컬럼이 없는 경우 (id 컬럼을 직접 사용)
                        query = f"SELECT * FROM {table} WHERE id = $1"
                        table_data = await conn.fetch(query, company_id)
                    
                    data[table] = [dict(row) for row in table_data]
                    
                except Exception as e:
                    logger.warning(f"테이블 {table} 데이터 조회 실패: {str(e)}")
                    data[table] = []
            
            await self.pool.release(conn)
            
            return {
                "company_name": company_name,
                "company_id": company_id,
                "found_in_table": found_table,
                "total_records": sum(len(v) for v in data.values()),
                "tables": list(data.keys()),
                "data": data
            }
            
        except Exception as e:
            logger.error(f"회사별 재무정보 조회 실패: {str(e)}")
            raise Exception(f"회사별 재무정보 조회 실패: {str(e)}")
    
    async def get_company_financial_summary(self, company_name: str) -> Dict[str, Any]:
        """특정 회사의 재무요약 정보 조회"""
        try:
            conn = await self.get_connection()
            
            # 1단계: companyname으로 회사 ID 찾기
            company_id = None
            found_table = None
            
            tables_to_search = ['employee', 'profit_loss', 'executives', 'financial_status', 'all_corporations']
            
            for table in tables_to_search:
                try:
                    check_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'companyname'"
                    has_companyname = await conn.fetch(check_query)
                    
                    if has_companyname:
                        search_query = f"SELECT id, companyname FROM {table} WHERE companyname ILIKE $1 LIMIT 1"
                        result = await conn.fetch(search_query, f"%{company_name}%")
                        
                        if result:
                            company_id = result[0]['id']
                            found_table = table
                            break
                except Exception as e:
                    continue
            
            if not company_id:
                await self.pool.release(conn)
                return {
                    "company_name": company_name,
                    "message": "해당 회사를 찾을 수 없습니다",
                    "summary": {}
                }
            
            # 2단계: 요약 정보 생성
            summary = {
                "company_info": {
                    "id": company_id,
                    "name": company_name,
                    "found_in_table": found_table
                },
                "financial_metrics": {},
                "employee_count": 0,
                "executive_count": 0
            }
            
            # 각 테이블에서 company_id로 데이터 개수 및 요약 조회
            for table in tables_to_search:
                try:
                    check_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'company_id'"
                    has_company_id = await conn.fetch(check_query)
                    
                    if has_company_id:
                        # company_id 컬럼이 있는 경우
                        count_query = f"SELECT COUNT(*) as count FROM {table} WHERE company_id = $1"
                        count = await conn.fetchval(count_query, company_id)
                        
                        # 최신 데이터 조회 (date 컬럼이 있는 경우)
                        try:
                            latest_query = f"SELECT * FROM {table} WHERE company_id = $1 ORDER BY date DESC LIMIT 1"
                            latest_data = await conn.fetch(latest_query, company_id)
                            if latest_data:
                                summary["financial_metrics"][f"latest_{table}"] = dict(latest_data[0])
                        except:
                            # date 컬럼이 없는 경우 첫 번째 데이터
                            first_query = f"SELECT * FROM {table} WHERE company_id = $1 LIMIT 1"
                            first_data = await conn.fetch(first_query, company_id)
                            if first_data:
                                summary["financial_metrics"][f"sample_{table}"] = dict(first_data[0])
                        
                        # 특별한 테이블 처리
                        if table == 'employee':
                            summary["employee_count"] = count
                        elif table == 'executives':
                            summary["executive_count"] = count
                            
                    else:
                        # company_id 컬럼이 없는 경우 (id 컬럼을 직접 사용)
                        count_query = f"SELECT COUNT(*) as count FROM {table} WHERE id = $1"
                        count = await conn.fetchval(count_query, company_id)
                        
                        if table == 'employee':
                            summary["employee_count"] = count
                        elif table == 'executives':
                            summary["executive_count"] = count
                            
                except Exception as e:
                    logger.warning(f"테이블 {table} 요약 조회 실패: {str(e)}")
            
            await self.pool.release(conn)
            
            return {
                "company_name": company_name,
                "company_id": company_id,
                "found_in_table": found_table,
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"회사별 재무요약 조회 실패: {str(e)}")
            raise Exception(f"회사별 재무요약 조회 실패: {str(e)}")
    
    async def get_all_companies(self) -> List[Dict[str, Any]]:
        """등록된 모든 회사 목록 조회 (companyname 기준)"""
        try:
            conn = await self.get_connection()
            
            # 모든 테이블에서 companyname이 있는 테이블 찾기
            companies = []
            tables_to_search = ['employee', 'profit_loss', 'executives', 'financial_status', 'all_corporations']
            
            for table in tables_to_search:
                try:
                    # companyname 컬럼이 있는지 확인
                    check_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND column_name = 'companyname'"
                    has_companyname = await conn.fetch(check_query)
                    
                    if has_companyname:
                        # companyname 컬럼이 있는 테이블에서 회사 목록 조회
                        query = f"SELECT DISTINCT id, companyname FROM {table} WHERE companyname IS NOT NULL AND companyname != '' ORDER BY companyname"
                        table_companies = await conn.fetch(query)
                        
                        for row in table_companies:
                            company_info = {
                                'id': row['id'],
                                'name': row['companyname'],
                                'source_table': table
                            }
                            
                            # 중복 제거 (같은 회사명이 여러 테이블에 있을 수 있음)
                            if not any(c['name'] == company_info['name'] for c in companies):
                                companies.append(company_info)
                                
                except Exception as e:
                    logger.warning(f"테이블 {table}에서 회사 목록 조회 실패: {str(e)}")
                    continue
            
            await self.pool.release(conn)
            
            # 회사명으로 정렬
            companies.sort(key=lambda x: x['name'])
            
            return companies
            
        except Exception as e:
            logger.error(f"회사 목록 조회 실패: {str(e)}")
            raise Exception(f"회사 목록 조회 실패: {str(e)}")
    
    async def get_all_financial_data(self) -> Dict[str, Any]:
        """5개 테이블의 모든 재무 데이터 조회"""
        try:
            conn = await self.get_connection()
            
            # 5개 테이블 데이터 조회
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
            executives_query = "SELECT * FROM executives LIMIT 100"
            executives_data = await conn.fetch(executives_query)
            data['executives'] = [dict(row) for row in executives_data]
            
            # 4. 재무상태 테이블
            financial_status_query = "SELECT * FROM financial_status LIMIT 100"
            financial_status_data = await conn.fetch(financial_status_query)
            data['financial_status'] = [dict(row) for row in financial_status_data]
            
            # 5. 전체기업 테이블
            all_corporations_query = "SELECT * FROM all_corporations LIMIT 100"
            all_corporations_data = await conn.fetch(all_corporations_query)
            data['all_corporations'] = [dict(row) for row in all_corporations_data]
            
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
            elif table_name == 'executives':
                result = await self._insert_executives(conn, data)
            elif table_name == 'financial_status':
                result = await self._insert_financial_status(conn, data)
            elif table_name == 'all_corporations':
                result = await self._insert_all_corporations(conn, data)
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
            INSERT INTO employee (id, corp_code, companyname, sexdstn, fo_bbm, rgllbr_co, rgllbr_abacpt_labrr_co, cnttk_co, cnttk_abacpt_labrr_co, sm, avrg_)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('corp_code'),
            data.get('companyname'),
            data.get('sexdstn'),
            data.get('fo_bbm'),
            data.get('rgllbr_co'),
            data.get('rgllbr_abacpt_labrr_co'),
            data.get('cnttk_co'),
            data.get('cnttk_abacpt_labrr_co'),
            data.get('sm'),
            data.get('avrg_')
        )
        return {"message": "직원 데이터 생성 완료", "table": "employee"}
    
    async def _insert_profit_loss(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """손익계산 데이터 삽입"""
        query = """
            INSERT INTO profit_loss (id, companyname, metric_name, fiscal_year_current, fiscal_year_previous, fiscal_year_before_last)
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('companyname'),
            data.get('metric_name'),
            data.get('fiscal_year_current'),
            data.get('fiscal_year_previous'),
            data.get('fiscal_year_before_last')
        )
        return {"message": "손익계산 데이터 생성 완료", "table": "profit_loss"}
    
    async def _insert_executives(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """임원 데이터 삽입"""
        query = """
            INSERT INTO executives (id, corp_code, companyname, nm, sexdstn, birth_ym, ofcps, rgist_exctv_at, fte_at, chrg_job)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('corp_code'),
            data.get('companyname'),
            data.get('nm'),
            data.get('sexdstn'),
            data.get('birth_ym'),
            data.get('ofcps'),
            data.get('rgist_exctv_at'),
            data.get('fte_at'),
            data.get('chrg_job')
        )
        return {"message": "임원 데이터 생성 완료", "table": "executives"}
    
    async def _insert_financial_status(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """재무상태 데이터 삽입"""
        # financial_status 테이블의 실제 컬럼 구조를 확인할 수 없어서 기본 구조 유지
        query = """
            INSERT INTO financial_status (id, companyname, assets, liabilities, equity, date)
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('companyname'),
            data.get('assets'),
            data.get('liabilities'),
            data.get('equity'),
            data.get('date')
        )
        return {"message": "재무상태 데이터 생성 완료", "table": "financial_status"}
    
    async def _insert_all_corporations(self, conn, data: Dict[str, Any]) -> Dict[str, Any]:
        """전체기업 데이터 삽입"""
        query = """
            INSERT INTO all_corporations (id, stock_code, companyname, market, dart_code)
            VALUES ($1, $2, $3, $4, $5)
        """
        await conn.execute(
            query,
            data.get('id'),
            data.get('stock_code'),
            data.get('companyname'),
            data.get('market'),
            data.get('dart_code')
        )
        return {"message": "전체기업 데이터 생성 완료", "table": "all_corporations"}
    
    async def close(self):
        """리소스 정리"""
        if self.pool:
            await self.pool.close()
