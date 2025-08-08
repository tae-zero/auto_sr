import hashlib
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.common.models import User

logger = logging.getLogger("auth_service")

class LoginService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, auth_id: str, auth_pw: str) -> dict:
        try:
            # auth_id로 사용자 조회
            user_query = select(User).where(User.auth_id == auth_id)
            user_result = await db.execute(user_query)
            user = user_result.scalar_one_or_none()

            if not user:
                return {"success": False, "message": "존재하지 않는 인증 ID입니다."}

            # 비밀번호 해시화하여 비교
            hashed_password = hashlib.sha256(auth_pw.encode()).hexdigest()

            if user.auth_pw != hashed_password:
                return {"success": False, "message": "비밀번호가 일치하지 않습니다."}

            logger.info(f"✅ 로그인 성공: {user.email} (ID: {user.id})")
            return {
                "success": True,
                "message": "로그인이 완료되었습니다.",
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "company_id": user.company_id
            }
        except Exception as e:
            logger.error(f"❌ 로그인 처리 중 오류: {str(e)}")
            return {"success": False, "message": f"로그인 처리 중 오류가 발생했습니다: {str(e)}"}
