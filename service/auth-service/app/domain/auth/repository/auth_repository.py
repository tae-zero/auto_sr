"""
Auth Service Auth 리포지토리
- 인증 데이터 접근 및 관리
- 사용자 세션 및 인증 정보 저장
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from app.domain.auth.entity.auth_entity import AuthEntity, UserEntity

logger = logging.getLogger(__name__)

class AuthRepository:
    def __init__(self):
        # 메모리 기반 세션 저장소 (실제로는 Redis나 DB 사용)
        self.user_sessions = {}
        self.auth_data = {}
    
    async def save_auth_data(self, auth_entity: AuthEntity) -> bool:
        """인증 데이터 저장"""
        try:
            self.auth_data[auth_entity.user_id] = {
                "user_id": auth_entity.user_id,
                "email": auth_entity.email,
                "company_id": auth_entity.company_id,
                "status": auth_entity.status,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            return True
        except Exception as e:
            logger.error(f"인증 데이터 저장 실패: {str(e)}")
            raise Exception(f"인증 데이터 저장 실패: {str(e)}")
    
    async def get_auth_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """인증 데이터 조회"""
        try:
            return self.auth_data.get(user_id)
        except Exception as e:
            logger.error(f"인증 데이터 조회 실패: {str(e)}")
            raise Exception(f"인증 데이터 조회 실패: {str(e)}")
    
    async def save_user_session(self, user_entity: UserEntity) -> bool:
        """사용자 세션 저장"""
        try:
            session_token = f"session_{user_entity.auth_id}_{datetime.utcnow().timestamp()}"
            self.user_sessions[session_token] = {
                "auth_id": user_entity.auth_id,
                "email": user_entity.email,
                "status": user_entity.status,
                "created_at": datetime.utcnow().isoformat()
            }
            return True
        except Exception as e:
            logger.error(f"사용자 세션 저장 실패: {str(e)}")
            raise Exception(f"사용자 세션 저장 실패: {str(e)}")
    
    async def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """세션 토큰으로 사용자 정보 조회"""
        try:
            return self.user_sessions.get(session_token)
        except Exception as e:
            logger.error(f"사용자 세션 조회 실패: {str(e)}")
            raise Exception(f"사용자 세션 조회 실패: {str(e)}")
    
    async def delete_user_session(self, session_token: str) -> bool:
        """사용자 세션 삭제"""
        try:
            if session_token in self.user_sessions:
                del self.user_sessions[session_token]
                return True
            return False
        except Exception as e:
            logger.error(f"사용자 세션 삭제 실패: {str(e)}")
            raise Exception(f"사용자 세션 삭제 실패: {str(e)}")
    
    async def update_auth_status(self, user_id: str, status: str) -> bool:
        """인증 상태 업데이트"""
        try:
            if user_id in self.auth_data:
                self.auth_data[user_id]["status"] = status
                self.auth_data[user_id]["updated_at"] = datetime.utcnow().isoformat()
                return True
            return False
        except Exception as e:
            logger.error(f"인증 상태 업데이트 실패: {str(e)}")
            raise Exception(f"인증 상태 업데이트 실패: {str(e)}")
    
    async def get_all_sessions(self) -> List[Dict[str, Any]]:
        """모든 세션 조회"""
        try:
            return list(self.user_sessions.values())
        except Exception as e:
            logger.error(f"모든 세션 조회 실패: {str(e)}")
            raise Exception(f"모든 세션 조회 실패: {str(e)}")
    
    async def cleanup_expired_sessions(self, hours: int = 24) -> int:
        """만료된 세션 정리"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            expired_sessions = []
            for token, session_data in self.user_sessions.items():
                created_at = datetime.fromisoformat(session_data["created_at"])
                if created_at < cutoff_time:
                    expired_sessions.append(token)
            
            for token in expired_sessions:
                del self.user_sessions[token]
            
            logger.info(f"{len(expired_sessions)}개의 만료된 세션이 정리되었습니다")
            return len(expired_sessions)
            
        except Exception as e:
            logger.error(f"만료된 세션 정리 실패: {str(e)}")
            raise Exception(f"만료된 세션 정리 실패: {str(e)}")
    
    async def close(self):
        """리소스 정리"""
        # 필요한 경우 DB 연결 종료 등
        pass
