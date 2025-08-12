from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, List, Optional
import logging
import httpx
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# Auth Service URL 설정
AUTH_SERVICE_URL = os.getenv("RAILWAY_AUTH_SERVICE_URL", "http://localhost:8008")

@router.get("/auth/health",
    summary="Auth Service 상태 확인",
    description="Auth Service의 health endpoint를 호출하여 상태를 확인합니다.",
    response_description="Auth Service 상태",
    tags=["인증 서비스"]
)
async def auth_health_check():
    """Auth Service health check 프록시"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/health")
            return {
                "gateway_status": "healthy",
                "auth_service_status": response.json(),
                "auth_service_url": AUTH_SERVICE_URL
            }
    except Exception as e:
        logger.error(f"Auth Service 연결 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Auth Service 연결 실패: {str(e)}")

@router.post("/auth/login",
    summary="로그인",
    description="Auth Service를 통해 사용자 로그인을 처리합니다.",
    response_description="로그인 결과",
    tags=["인증 서비스"]
)
async def login_proxy(request: Request):
    """로그인 프록시 - Auth Service로 요청 전달"""
    try:
        # 요청 본문 읽기
        body = await request.body()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/login",
                content=body,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
    except Exception as e:
        logger.error(f"로그인 프록시 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"로그인 처리 실패: {str(e)}")

@router.post("/auth/signup",
    summary="회원가입",
    description="Auth Service를 통해 사용자 회원가입을 처리합니다.",
    response_description="회원가입 결과",
    tags=["인증 서비스"]
)
async def signup_proxy(request: Request):
    """회원가입 프록시 - Auth Service로 요청 전달"""
    try:
        # 요청 본문 읽기
        body = await request.body()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{AUTH_SERVICE_URL}/signup",
                content=body,
                headers={"Content-Type": "application/json"}
            )
            return response.json()
    except Exception as e:
        logger.error(f"회원가입 프록시 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"회원가입 처리 실패: {str(e)}")

@router.get("/auth/test",
    summary="Auth Service 테스트",
    description="Auth Service의 test endpoint를 호출합니다.",
    response_description="테스트 결과",
    tags=["인증 서비스"]
)
async def auth_test():
    """Auth Service test endpoint 프록시"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/test")
            return {
                "gateway_message": "Gateway를 통한 Auth Service 테스트",
                "auth_service_response": response.json()
            }
    except Exception as e:
        logger.error(f"Auth Service 테스트 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Auth Service 테스트 실패: {str(e)}")

# 기존 사용자 관리 엔드포인트들 (Auth Service로 프록시)
@router.get("/users",
    summary="사용자 목록 조회",
    description="Auth Service를 통해 등록된 모든 사용자의 목록을 조회합니다.",
    response_description="사용자 목록",
    tags=["사용자 관리"]
)
async def get_users():
    """사용자 목록 조회 (Auth Service로 프록시)"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/users")
            return response.json()
    except Exception as e:
        logger.error(f"사용자 목록 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"사용자 목록 조회 실패: {str(e)}")

@router.get("/users/{user_id}",
    summary="특정 사용자 조회",
    description="Auth Service를 통해 지정된 ID의 사용자 정보를 조회합니다.",
    response_description="사용자 정보",
    tags=["사용자 관리"]
)
async def get_user(user_id: str):
    """특정 사용자 조회 (Auth Service로 프록시)"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/users/{user_id}")
            return response.json()
    except Exception as e:
        logger.error(f"사용자 조회 실패: {str(e)}")
        raise HTTPException(status_code=503, detail=f"사용자 조회 실패: {str(e)}")
