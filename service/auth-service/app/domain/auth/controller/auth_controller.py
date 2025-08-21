"""
Auth Service Auth 컨트롤러
- 인증 관련 API 엔드포인트
- 요청/응답 처리 및 검증
- 로그인 및 회원가입 처리
"""
from fastapi import APIRouter, HTTPException, Request, Depends, Header
from typing import Dict, Any, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.auth.service.auth_service import AuthService
from app.domain.auth.model.auth_model import LoginRequest, SignupRequest, AuthResponse
from app.domain.auth.schema.auth_schema import UserProfile, LogoutResponse
from app.common.database.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["인증"])

@router.get("/health")
async def health_check():
    """Auth Service 상태 확인"""
    return {
        "status": "healthy",
        "service": "auth-service",
        "architecture": "MSV Pattern with Layered Architecture",
        "layers": [
            "Controller Layer - API 엔드포인트",
            "Service Layer - 비즈니스 로직",
            "Repository Layer - 데이터 접근",
            "Entity Layer - 데이터베이스 엔티티",
            "Model Layer - Pydantic 모델",
            "Schema Layer - 데이터 스키마"
        ]
    }

@router.post("/login", response_model=AuthResponse)
async def login(request: Request, db: AsyncSession = Depends(get_db)):
    """로그인 처리"""
    try:
        # 요청 본문에서 formData 읽기
        form_data = await request.json()
        logger.info(f"🔐 로그인 시도: {form_data.get('auth_id', 'N/A')}")
        
        # 필수 필드 검증
        required_fields = ['auth_id', 'auth_pw']
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        
        if missing_fields:
            logger.warning(f"필수 필드 누락: {missing_fields}")
            raise HTTPException(status_code=400, detail=f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}")
        
        # Auth Service를 통한 인증
        auth_service = AuthService()
        login_request = LoginRequest(
            auth_id=form_data['auth_id'],
            auth_pw=form_data['auth_pw']
        )
        
        result = await auth_service.authenticate_user(db, login_request)
        return AuthResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그인 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}")

@router.post("/signup", response_model=AuthResponse)
async def signup(request: Request, db: AsyncSession = Depends(get_db)):
    """회원가입 처리"""
    try:
        # 요청 본문에서 formData 읽기
        form_data = await request.json()
        logger.info("📝 회원가입 POST 요청 받음")
        
        # 필수 필드 검증
        required_fields = ['company_id', 'industry', 'email', 'name', 'age', 'auth_id', 'auth_pw']
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        
        if missing_fields:
            logger.warning(f"필수 필드 누락: {missing_fields}")
            raise HTTPException(status_code=400, detail=f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}")
        
        # 새로운 컬럼명에 맞춰 로그 출력
        logger.info("=== 회원가입 요청 데이터 ===")
        logger.info(f"회사 ID: {form_data.get('company_id', 'N/A')}")
        logger.info(f"산업: {form_data.get('industry', 'N/A')}")
        logger.info(f"이메일: {form_data.get('email', 'N/A')}")
        logger.info(f"이름: {form_data.get('name', 'N/A')}")
        logger.info(f"나이: {form_data.get('age', 'N/A')}")
        logger.info(f"인증 ID: {form_data.get('auth_id', 'N/A')}")
        logger.info(f"인증 비밀번호: [PROTECTED]")
        logger.info("==========================")
        
        # Auth Service를 통한 회원가입
        auth_service = AuthService()
        signup_request = SignupRequest(**form_data)
        
        result = await auth_service.create_user(db, signup_request)
        return AuthResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회원가입 처리 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"회원가입 처리 중 오류가 발생했습니다: {str(e)}")

@router.get("/profile", response_model=UserProfile)
async def get_profile(session_token: str = None):
    """사용자 프로필 조회"""
    try:
        if not session_token:
            raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다")
        
        auth_service = AuthService()
        profile = await auth_service.get_user_profile(session_token)
        return UserProfile(**profile)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로필 조회 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/verify")
async def verify_token_endpoint(authorization: str = Header(None)):
    """토큰 검증 엔드포인트"""
    try:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        token = authorization.replace('Bearer ', '')
        
        from app.domain.auth.utils.jwt_utils import verify_token
        
        # 토큰 검증
        result = verify_token(token)
        
        if not result.get('valid'):
            raise HTTPException(status_code=401, detail=result.get('message', '토큰이 유효하지 않습니다'))
        
        # 검증 성공 시 사용자 정보 반환
        user_info = result.get('user_info', {})
        return {
            "success": True,
            "message": "토큰이 유효합니다",
            "user_info": user_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"토큰 검증 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="토큰 검증 중 오류가 발생했습니다")

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(authorization: str = Header(None)):
    """토큰 갱신 처리"""
    try:
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=400, detail="Bearer 토큰이 필요합니다")
        
        token = authorization.replace('Bearer ', '')
        
        from app.domain.auth.utils.jwt_utils import verify_token, create_token
        
        # 토큰 검증
        result = verify_token(token)
        
        if not result.get('valid'):
            raise HTTPException(status_code=401, detail=result.get('message', '토큰이 유효하지 않습니다'))
        
        # 새 토큰 생성
        user_info = result.get('user_info', {})
        new_token = create_token(user_info)
        
        return AuthResponse(
            success=True,
            message="토큰이 갱신되었습니다",
            access_token=new_token,
            email=user_info.get('email'),
            name=user_info.get('name'),
            company_id=user_info.get('company_id')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"토큰 갱신 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout", response_model=LogoutResponse)
async def logout(session_token: str = None):
    """로그아웃 처리"""
    try:
        auth_service = AuthService()
        result = await auth_service.logout_user(session_token)
        return LogoutResponse(**result)
        
    except Exception as e:
        logger.error(f"로그아웃 처리 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
