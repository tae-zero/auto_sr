"""
User Repository
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.user.user_model import UserModel

class UserRepository:
    """사용자 리포지토리"""
    
    @staticmethod
    async def find_by_email(db: AsyncSession, email: str):
        """이메일로 사용자 조회"""
        query = select(UserModel).where(UserModel.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def find_by_auth_id(db: AsyncSession, auth_id: str):
        """인증 ID로 사용자 조회"""
        query = select(UserModel).where(UserModel.auth_id == auth_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
