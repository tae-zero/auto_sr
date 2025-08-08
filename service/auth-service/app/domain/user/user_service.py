"""
User Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user.user_repository import UserRepository

class UserService:
    """사용자 서비스"""
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        """이메일로 사용자 조회"""
        return await UserRepository.find_by_email(db, email)
    
    @staticmethod
    async def get_user_by_auth_id(db: AsyncSession, auth_id: str):
        """인증 ID로 사용자 조회"""
        return await UserRepository.find_by_auth_id(db, auth_id)
