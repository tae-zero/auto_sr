from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
import hashlib
import logging
from datetime import datetime

from app.common.models import User

logger = logging.getLogger(__name__)

class SignupService:
    """회원가입 서비스"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """비밀번호 해시화"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    async def check_email_exists(db: AsyncSession, email: str) -> bool:
        """이메일 중복 확인"""
        try:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            return user is not None
        except Exception as e:
            logger.error(f"이메일 중복 확인 오류: {str(e)}")
            return False
    
    @staticmethod
    async def check_auth_id_exists(db: AsyncSession, auth_id: str) -> bool:
        """인증 ID 중복 확인"""
        try:
            result = await db.execute(select(User).where(User.auth_id == auth_id))
            user = result.scalar_one_or_none()
            return user is not None
        except Exception as e:
            logger.error(f"인증 ID 중복 확인 오류: {str(e)}")
            return False
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict) -> dict:
        """사용자 생성"""
        try:
            # 중복 확인
            email_exists = await SignupService.check_email_exists(db, user_data["email"])
            if email_exists:
                return {"success": False, "message": "이미 존재하는 이메일입니다."}
            
            auth_id_exists = await SignupService.check_auth_id_exists(db, user_data["auth_id"])
            if auth_id_exists:
                return {"success": False, "message": "이미 존재하는 인증 ID입니다."}
            
            # 비밀번호 해시화
            hashed_password = SignupService.hash_password(user_data["auth_pw"])
            
            # 사용자 생성
            new_user = User(
                company_id=user_data["company_id"],
                industry=user_data["industry"],
                email=user_data["email"],
                name=user_data["name"],
                age=user_data["age"],
                auth_id=user_data["auth_id"],
                auth_pw=hashed_password
            )
            
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            
            logger.info(f"✅ 사용자 생성 성공: {new_user.email} (ID: {new_user.id})")
            
            return {
                "success": True,
                "message": "회원가입이 완료되었습니다.",
                "user_id": new_user.id,
                "email": new_user.email
            }
            
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"데이터베이스 무결성 오류: {str(e)}")
            return {"success": False, "message": "중복된 데이터가 있습니다."}
        
        except Exception as e:
            await db.rollback()
            logger.error(f"사용자 생성 오류: {str(e)}")
            return {"success": False, "message": f"회원가입 중 오류가 발생했습니다: {str(e)}"}
