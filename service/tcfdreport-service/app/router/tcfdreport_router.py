from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
import asyncpg
import os
from datetime import datetime

logger = logging.getLogger(__name__)

tcfdreport_router = APIRouter()

# 데이터베이스 연결 함수
async def get_db_connection():
    """데이터베이스 연결 반환"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise Exception("DATABASE_URL 환경변수가 설정되지 않았습니다")
        
        # URL 스키마 수정
        if database_url.startswith("postgresql+asyncpg://"):
            database_url = "postgresql://" + database_url[len("postgresql+asyncpg://"):]
        elif database_url.startswith("postgres://"):
            database_url = "postgresql://" + database_url[len("postgres://"):]
        
        conn = await asyncpg.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {str(e)}")
        raise

@tcfdreport_router.get("/")
async def root():
    return {"message": "TCFD Report Service"}

@tcfdreport_router.get("/health")
async def health_check():
    return {"status": "healthy"}

@tcfdreport_router.post("/inputs")
async def create_tcfd_inputs(data: Dict[str, Any]):
    """TCFD 입력 데이터 생성"""
    conn = None
    try:
        logger.info(f"TCFD 입력 데이터 생성 요청: {data}")
        
        # 필수 필드 검증
        if not data.get('company_name'):
            raise HTTPException(status_code=400, detail="회사명은 필수입니다")
        if not data.get('user_id'):
            raise HTTPException(status_code=400, detail="사용자 ID는 필수입니다")
        
        # 데이터베이스 연결
        conn = await get_db_connection()
        
        # 입력된 필드만 추출하여 저장
        fields_to_insert = ['company_name', 'user_id']
        values_to_insert = [data['company_name'], data['user_id']]
        
        # 선택적 필드들 (입력된 경우에만 저장)
        optional_fields = [
            'governance_g1', 'governance_g2',
            'strategy_s1', 'strategy_s2', 'strategy_s3',
            'risk_management_r1', 'risk_management_r2', 'risk_management_r3',
            'metrics_targets_m1', 'metrics_targets_m2', 'metrics_targets_m3'
        ]
        
        for field in optional_fields:
            if data.get(field) and data[field].strip():  # 빈 문자열이 아닌 경우에만
                fields_to_insert.append(field)
                values_to_insert.append(data[field])
        
        # SQL 쿼리 생성
        placeholders = ', '.join([f'${i+1}' for i in range(len(values_to_insert))])
        fields_str = ', '.join(fields_to_insert)
        
        query = f"""
            INSERT INTO tcfd_inputs ({fields_str}, created_at, updated_at)
            VALUES ({placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, company_name, created_at
        """
        
        # 데이터 저장
        result = await conn.fetchrow(query, *values_to_insert)
        
        logger.info(f"TCFD 입력 데이터 저장 성공: ID={result['id']}, 회사={result['company_name']}")
        
        return {
            "success": True,
            "message": "TCFD 입력 데이터가 성공적으로 저장되었습니다",
            "data": {
                "id": result['id'],
                "company_name": result['company_name'],
                "user_id": data['user_id'],
                "created_at": result['created_at'].isoformat(),
                "saved_fields": fields_to_insert
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TCFD 입력 데이터 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터 저장 실패: {str(e)}")
    finally:
        if conn:
            await conn.close()

@tcfdreport_router.get("/inputs/{company_name}")
async def get_tcfd_inputs(company_name: str):
    """회사별 TCFD 입력 데이터 조회"""
    conn = None
    try:
        logger.info(f"TCFD 입력 데이터 조회 요청: {company_name}")
        
        # 데이터베이스 연결
        conn = await get_db_connection()
        
        # 최신 데이터 조회
        query = """
            SELECT * FROM tcfd_inputs 
            WHERE company_name = $1 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        result = await conn.fetchrow(query, company_name)
        
        if not result:
            return {
                "success": True,
                "company_name": company_name,
                "message": "해당 회사의 TCFD 데이터가 없습니다",
                "data": {
                    "governance_g1": "",
                    "governance_g2": "",
                    "strategy_s1": "",
                    "strategy_s2": "",
                    "strategy_s3": "",
                    "risk_management_r1": "",
                    "risk_management_r2": "",
                    "risk_management_r3": "",
                    "metrics_targets_m1": "",
                    "metrics_targets_m2": "",
                    "metrics_targets_m3": ""
                }
            }
        
        # 데이터베이스 결과를 딕셔너리로 변환
        data = {
            "governance_g1": result.get('governance_g1', ''),
            "governance_g2": result.get('governance_g2', ''),
            "strategy_s1": result.get('strategy_s1', ''),
            "strategy_s2": result.get('strategy_s2', ''),
            "strategy_s3": result.get('strategy_s3', ''),
            "risk_management_r1": result.get('risk_management_r1', ''),
            "risk_management_r2": result.get('risk_management_r2', ''),
            "risk_management_r3": result.get('risk_management_r3', ''),
            "metrics_targets_m1": result.get('metrics_targets_m1', ''),
            "metrics_targets_m2": result.get('metrics_targets_m2', ''),
            "metrics_targets_m3": result.get('metrics_targets_m3', '')
        }
        
        logger.info(f"TCFD 입력 데이터 조회 성공: 회사={company_name}")
        
        return {
            "success": True,
            "company_name": company_name,
            "data": data,
            "metadata": {
                "id": result['id'],
                "user_id": result.get('user_id'),
                "created_at": result['created_at'].isoformat(),
                "updated_at": result['updated_at'].isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"TCFD 입력 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    finally:
        if conn:
            await conn.close()