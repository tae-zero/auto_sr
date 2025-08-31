#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV 파일들을 Railway PostgreSQL 데이터베이스에 로드하는 스크립트
기후 시나리오 데이터를 데이터베이스에 저장
"""

import pandas as pd
import os
import asyncio
import asyncpg
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ClimateDataLoader:
    def __init__(self):
        self.connection = None
        self.pool = None
        
    async def connect_to_database(self):
        """Railway PostgreSQL 데이터베이스에 연결"""
        try:
            # 환경변수에서 데이터베이스 URL 가져오기
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise ValueError("DATABASE_URL 환경변수가 설정되지 않았습니다.")
            
            # Railway 환경에서는 postgresql:// 스키마 사용
            if database_url.startswith('postgresql+asyncpg://'):
                database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
            
            logger.info(f"🔗 데이터베이스 연결 중: {database_url.split('@')[1] if '@' in database_url else 'Unknown'}")
            
            # 연결 풀 생성
            self.pool = await asyncpg.create_pool(database_url)
            logger.info("✅ 데이터베이스 연결 성공")
            
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {str(e)}")
            raise
    
    async def create_tables(self):
        """기후 데이터 테이블들 생성"""
        try:
            conn = await self.pool.acquire()
            
            # 기존 테이블이 있다면 삭제 (테스트용)
            await conn.execute("DROP TABLE IF EXISTS climate_data CASCADE")
            await conn.execute("DROP TABLE IF EXISTS administrative_regions CASCADE")
            await conn.execute("DROP TABLE IF EXISTS climate_variables CASCADE")
            await conn.execute("DROP TABLE IF EXISTS climate_scenarios CASCADE")
            
            # 기후 시나리오 테이블
            await conn.execute("""
                CREATE TABLE climate_scenarios (
                    id SERIAL PRIMARY KEY,
                    scenario_code VARCHAR(20) UNIQUE NOT NULL,
                    scenario_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 기후 변수 테이블
            await conn.execute("""
                CREATE TABLE climate_variables (
                    id SERIAL PRIMARY KEY,
                    variable_code VARCHAR(20) UNIQUE NOT NULL,
                    variable_name VARCHAR(100) NOT NULL,
                    unit VARCHAR(50) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 행정구역 테이블
            await conn.execute("""
                CREATE TABLE administrative_regions (
                    id SERIAL PRIMARY KEY,
                    region_code VARCHAR(20) UNIQUE NOT NULL,
                    region_name VARCHAR(100) NOT NULL,
                    sub_region_name VARCHAR(100) UNIQUE NOT NULL,
                    parent_region VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 기후 데이터 테이블
            await conn.execute("""
                CREATE TABLE climate_data (
                    id SERIAL PRIMARY KEY,
                    scenario_id INTEGER REFERENCES climate_scenarios(id),
                    variable_id INTEGER REFERENCES climate_variables(id),
                    region_id INTEGER REFERENCES administrative_regions(id),
                    year INTEGER NOT NULL,
                    value FLOAT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 인덱스 생성
            await conn.execute("""
                CREATE INDEX idx_climate_data_lookup 
                ON climate_data(scenario_id, variable_id, region_id, year)
            """)
            
            logger.info("✅ 테이블 생성 완료")
            
        except Exception as e:
            logger.error(f"❌ 테이블 생성 실패: {str(e)}")
            raise
        finally:
            await self.pool.release(conn)
    
    async def insert_master_data(self):
        """마스터 데이터 삽입"""
        try:
            conn = await self.pool.acquire()
            
            # 기후 시나리오 데이터
            scenarios = [
                ('SSP126', 'SSP1-2.6 (저탄소 시나리오)', 'IPCC AR6 SSP1-2.6 시나리오'),
                ('SSP585', 'SSP5-8.5 (고탄소 시나리오)', 'IPCC AR6 SSP5-8.5 시나리오')
            ]
            
            for scenario in scenarios:
                await conn.execute("""
                    INSERT INTO climate_scenarios (scenario_code, scenario_name, description)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (scenario_code) DO NOTHING
                """, *scenario)
            
            # 기후 변수 데이터
            variables = [
                ('HW33', '폭염일수', '일', '최고기온 33°C 이상인 일수'),
                ('RN', '연강수량', 'mm', '연간 총 강수량'),
                ('TA', '연평균기온', '°C', '연간 평균 기온'),
                ('TR25', '열대야일수', '일', '최저기온 25°C 이상인 일수'),
                ('RAIN80', '호우일수', '일', '일강수량 80mm 이상인 일수')
            ]
            
            for variable in variables:
                await conn.execute("""
                    INSERT INTO climate_variables (variable_code, variable_name, unit, description)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (variable_code) DO NOTHING
                """, *variable)
            
            logger.info("✅ 마스터 데이터 삽입 완료")
            
        except Exception as e:
            logger.error(f"❌ 마스터 데이터 삽입 실패: {str(e)}")
            raise
        finally:
            await self.pool.release(conn)
    
    async def load_csv_data(self, csv_file_path):
        """CSV 파일의 데이터를 데이터베이스에 로드"""
        try:
            logger.info(f"📄 CSV 파일 로드 중: {csv_file_path.name}")
            
            # CSV 파일 읽기
            df = pd.read_csv(csv_file_path)
            logger.info(f"📊 CSV 데이터: {len(df)}행, {len(df.columns)}컬럼")
            
            # 파일명에서 시나리오와 변수 추출
            filename = csv_file_path.stem
            if 'SSP126' in filename:
                scenario_code = 'SSP126'
            elif 'SSP585' in filename:
                scenario_code = 'SSP585'
            else:
                logger.warning(f"⚠️ 시나리오 코드를 찾을 수 없습니다: {filename}")
                return False
            
            if 'HW33' in filename:
                variable_code = 'HW33'
            elif 'RN' in filename:
                variable_code = 'RN'
            elif 'TA' in filename:
                variable_code = 'TA'
            elif 'TR25' in filename:
                variable_code = 'TR25'
            elif 'RAIN80' in filename:
                variable_code = 'RAIN80'
            else:
                logger.warning(f"⚠️ 변수 코드를 찾을 수 없습니다: {filename}")
                return False
            
            logger.info(f"🔍 시나리오: {scenario_code}, 변수: {variable_code}")
            
            conn = await self.pool.acquire()
            
            # 시나리오 ID와 변수 ID 가져오기
            scenario_id = await conn.fetchval(
                "SELECT id FROM climate_scenarios WHERE scenario_code = $1", 
                scenario_code
            )
            variable_id = await conn.fetchval(
                "SELECT id FROM climate_variables WHERE variable_code = $1", 
                variable_code
            )
            
            if not scenario_id or not variable_id:
                logger.error(f"❌ 시나리오 또는 변수 ID를 찾을 수 없습니다")
                return False
            
            # 고유한 행정구역명들 가져오기
            unique_regions = df['Sub_Region_Name'].unique()
            logger.info(f"🏘️ 고유 행정구역 수: {len(unique_regions)}")
            
            # 첫 번째 파일에서만 행정구역 데이터 삽입 (중복 방지)
            if 'HW33' in filename and 'SSP126' in filename:  # 첫 번째 파일만
                logger.info("🏗️ 행정구역 데이터 삽입 중...")
                for i, region_name in enumerate(unique_regions):
                    await conn.execute("""
                        INSERT INTO administrative_regions (region_code, region_name, sub_region_name)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (sub_region_name) DO NOTHING
                    """, f"REG_{i+1:03d}", "대한민국", region_name)
                logger.info("✅ 행정구역 데이터 삽입 완료")
            
            # 기후 데이터 삽입
            data_to_insert = []
            for _, row in df.iterrows():
                region_id = await conn.fetchval(
                    "SELECT id FROM administrative_regions WHERE sub_region_name = $1",
                    row['Sub_Region_Name']
                )
                
                if region_id:
                    data_to_insert.append((
                        scenario_id,
                        variable_id,
                        region_id,
                        int(row['Year']),
                        float(row['Climate_Value'])
                    ))
            
            # 배치 삽입
            if data_to_insert:
                await conn.executemany("""
                    INSERT INTO climate_data (scenario_id, variable_id, region_id, year, value)
                    VALUES ($1, $2, $3, $4, $5)
                """, data_to_insert)
                
                logger.info(f"✅ 데이터 삽입 완료: {len(data_to_insert)}행")
                return True
            else:
                logger.warning(f"⚠️ 삽입할 데이터가 없습니다")
                return False
                
        except Exception as e:
            logger.error(f"❌ CSV 데이터 로드 실패: {str(e)}")
            return False
        finally:
            if 'conn' in locals():
                await self.pool.release(conn)
    
    async def close_connection(self):
        """데이터베이스 연결 종료"""
        if self.pool:
            await self.pool.close()
            logger.info("🔌 데이터베이스 연결 종료")

async def main():
    """메인 함수"""
    loader = ClimateDataLoader()
    
    try:
        # 데이터베이스 연결
        await loader.connect_to_database()
        
        # 테이블 생성
        await loader.create_tables()
        
        # 마스터 데이터 삽입
        await loader.insert_master_data()
        
        # CSV 파일들 로드
        csv_files = list(Path(".").glob("*.csv"))
        logger.info(f"📋 발견된 CSV 파일: {len(csv_files)}개")
        
        success_count = 0
        for csv_file in csv_files:
            if await loader.load_csv_data(csv_file):
                success_count += 1
        
        logger.info(f"🎉 CSV 로드 완료: {success_count}/{len(csv_files)} 성공")
        
    except Exception as e:
        logger.error(f"❌ 메인 실행 실패: {str(e)}")
    finally:
        await loader.close_connection()

if __name__ == "__main__":
    asyncio.run(main())
