"""
Auth Service Auth 서비스
- 인증 비즈니스 로직 처리
- 로그인 및 회원가입 처리
- 사용자 인증 및 세션 관리
"""
from typing import Dict, Any, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.domain.auth.repository.auth_repository import AuthRepository
from app.domain.auth.model.auth_model import LoginRequest, SignupRequest
from app.domain.auth.entity.auth_entity import AuthEntity, UserEntity
from app.domain.auth.schema.auth_schema import UserProfile, LogoutResponse

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.repository = AuthRepository()
    
    async def authenticate_user(self, db: AsyncSession, request: LoginRequest) -> Dict[str, Any]:
        """사용자 인증 처리"""
        try:
            # 기존 LoginService 로직 통합
            from app.domain.auth.service.login_service import LoginService
            result = await LoginService.authenticate_user(db, request.auth_id, request.auth_pw)
            
            # 인증 성공 시 사용자 정보 저장
            if result.get("success"):
                user_entity = UserEntity(
                    auth_id=request.auth_id,
                    email=result.get("email", ""),
                    status="active"
                )
                await self.repository.save_user_session(user_entity)
            
            return result
            
        except Exception as e:
            logger.error(f"사용자 인증 실패: {str(e)}")
            raise Exception(f"인증 처리 실패: {str(e)}")
    
    async def create_user(self, db: AsyncSession, request: SignupRequest) -> Dict[str, Any]:
        """사용자 회원가입 처리"""
        try:
            # 기존 SignupService 로직 통합
            from app.domain.auth.service.signup_service import SignupService
            form_data = request.dict()
            result = await SignupService.create_user(db, form_data)
            
            # 회원가입 성공 시 사용자 엔티티 저장
            if result.get("success"):
                auth_entity = AuthEntity(
                    user_id=result.get("user_id"),
                    email=request.email,
                    company_id=request.company_id,
                    status="active"
                )
                await self.repository.save_auth_data(auth_entity)
            
            return result
            
        except Exception as e:
            logger.error(f"사용자 회원가입 실패: {str(e)}")
            raise Exception(f"회원가입 처리 실패: {str(e)}")
    
    async def get_user_profile(self, session_token: str) -> Dict[str, Any]:
        """사용자 프로필 조회"""
        try:
            # 세션 토큰으로 사용자 정보 조회
            user_data = await self.repository.get_user_by_session(session_token)
            
            if not user_data:
                raise HTTPException(status_code=401, detail="유효하지 않은 세션 토큰입니다")
            
            return {
                "user_id": user_data.get("user_id"),
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "company_id": user_data.get("company_id"),
                "status": user_data.get("status")
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"사용자 프로필 조회 실패: {str(e)}")
            raise Exception(f"프로필 조회 실패: {str(e)}")
    
    async def logout_user(self, session_token: str) -> Dict[str, Any]:
        """사용자 로그아웃 처리"""
        try:
            # 세션 토큰 삭제
            await self.repository.delete_user_session(session_token)
            
            return {
                "success": True,
                "message": "로그아웃되었습니다."
            }
            
        except Exception as e:
            logger.error(f"로그아웃 처리 실패: {str(e)}")
            raise Exception(f"로그아웃 처리 실패: {str(e)}")
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """토큰 검증"""
        try:
            # 토큰 검증 로직
            user_data = await self.repository.get_user_by_session(token)
            
            if not user_data:
                return {
                    "valid": False,
                    "message": "유효하지 않은 토큰입니다"
                }
            
            return {
                "valid": True,
                "user_info": user_data,
                "message": "토큰이 유효합니다"
            }
            
        except Exception as e:
            logger.error(f"토큰 검증 실패: {str(e)}")
            return {
                "valid": False,
                "message": f"토큰 검증 실패: {str(e)}"
            }
    
    async def close(self):
        """리소스 정리"""
        await self.repository.close()
