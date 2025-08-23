from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.responses import JSONResponse
import httpx
import os
import logging
from typing import Optional

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# ... existing code ...

# Auth Service URL 가져오기
def get_auth_service_url():
    """환경에 따른 Auth Service URL 반환"""
    railway_env = os.getenv("RAILWAY_ENVIRONMENT")
    if railway_env in ["true", "production"]:  # "production"도 인식
        return os.getenv("RAILWAY_AUTH_SERVICE_URL", "https://auth-service-production-1deb.up.railway.app")
    return os.getenv("AUTH_SERVICE_URL", "http://auth-service:8008")



@router.post("/login")
async def login(auth_data: dict):
    """로그인 엔드포인트"""
    max_retries = 3
    retry_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            auth_service_url = get_auth_service_url()
            
            logger.info(f"🔍 Auth Service로 로그인 요청 (시도 {attempt + 1}/{max_retries}): {auth_service_url}/api/v1/auth/login")
            logger.info(f"📤 요청 데이터: {auth_data}")
            
            # Auth Service로 로그인 요청
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{auth_service_url}/api/v1/auth/login",
                    json=auth_data
                )
                
                if response.status_code == 200:
                    logger.info("✅ 로그인 성공")
                    return response.json()
                else:
                    logger.error(f"❌ 로그인 실패: {response.status_code}")
                    raise HTTPException(status_code=response.status_code, detail="로그인 실패")
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 로그인 처리 오류 (시도 {attempt + 1}/{max_retries}): {str(e)}")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ {retry_delay}초 후 재시도...")
                import asyncio
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # 지수 백오프
            else:
                logger.error("❌ 모든 재시도 실패")
                raise HTTPException(status_code=500, detail="로그인 중 오류가 발생했습니다")

@router.get("/verify")
async def verify_token(authorization: str = Header(None)):
    """토큰 검증 엔드포인트"""
    try:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        token = authorization.replace('Bearer ', '')
        auth_service_url = get_auth_service_url()
        
        logger.info(f"🔍 Auth Service로 토큰 검증 요청: {auth_service_url}/api/v1/auth/verify")
        
        # Auth Service로 토큰 검증 요청
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{auth_service_url}/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                logger.info("✅ 토큰 검증 성공")
                return response.json()
            else:
                logger.error(f"❌ 토큰 검증 실패: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="토큰 검증 실패")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 토큰 검증 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="토큰 검증 중 오류가 발생했습니다")

@router.post("/refresh")
async def refresh_token(authorization: str = Header(None)):
    """토큰 갱신 엔드포인트"""
    try:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=400, detail="Bearer 토큰이 필요합니다")
        
        token = authorization.replace('Bearer ', '')
        auth_service_url = get_auth_service_url()
        
        logger.info(f"🔍 Auth Service로 토큰 갱신 요청: {auth_service_url}/api/v1/auth/refresh")
        
        # Auth Service로 토큰 갱신 요청
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{auth_service_url}/api/v1/auth/refresh",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code == 200:
                logger.info("✅ 토큰 갱신 성공")
                return response.json()
            else:
                logger.error(f"❌ 토큰 갱신 실패: {response.status_code}")
                raise HTTPException(status_code=response.status_code, detail="토큰 갱신 실패")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 토큰 갱신 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="토큰 갱신 중 오류가 발생했습니다")
