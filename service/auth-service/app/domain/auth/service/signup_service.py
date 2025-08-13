"""
Auth Service - Signup Service
"""
import hashlib
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.common.models import User

logger = logging.getLogger("auth_service")

class SignupService:
    """회원가입 서비스"""
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict) -> dict:
        """새 사용자를 생성합니다."""
        try:
            # 이메일 중복 확인
            email_query = select(User).where(User.email == user_data['email'])
            email_result = await db.execute(email_query)
            if email_result.scalar_one_or_none():
                return {
                    "success": False,
                    "message": "이미 존재하는 이메일입니다."
                }
            
            # 인증 ID 중복 확인
            auth_id_query = select(User).where(User.auth_id == user_data['auth_id'])
            auth_id_result = await db.execute(auth_id_query)
            if auth_id_result.scalar_one_or_none():
                return {
                    "success": False,
                    "message": "이미 존재하는 인증 ID입니다."
                }
            
            # 비밀번호 해시화 (SHA256)
            hashed_password = hashlib.sha256(user_data['auth_pw'].encode()).hexdigest()
            
            # 새 사용자 생성
            new_user = User(
                company_id=user_data['company_id'],
                industry=user_data['industry'],
                email=user_data['email'],
                name=user_data['name'],
                age=user_data['age'],
                auth_id=user_data['auth_id'],
                auth_pw=hashed_password
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            logger.info(f"✅ 새 사용자 생성 완료: {new_user.email} (ID: {new_user.id})")
            
            return {
                "success": True,
                "message": "회원가입이 완료되었습니다.",
                "user_id": new_user.id,  # 원래 정수값 그대로 반환
                "email": new_user.email
            }
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ 사용자 생성 중 오류: {str(e)}")
            return {
                "success": False,
                "message": f"회원가입 처리 중 오류가 발생했습니다: {str(e)}"
            }
