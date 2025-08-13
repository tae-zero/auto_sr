"""
Gateway Auth 리포지토리
- 인증 데이터 접근 및 관리
- 로그인 기록 및 상태 저장
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from app.domain.auth.entity.auth_entity import AuthEntity

logger = logging.getLogger(__name__)

class AuthRepository:
    def __init__(self):
        # 메모리 기반 저장소 (실제로는 데이터베이스 사용)
        self.auth_data = {}
        self.login_logs = []
    
    async def save_auth_data(self, auth_entity: AuthEntity) -> bool:
        """인증 데이터 저장"""
        try:
            self.auth_data[auth_entity.user_id] = {
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
    
    async def log_login_attempt(self, email: str, success: bool, timestamp: Optional[str] = None) -> bool:
        """로그인 시도 기록"""
        try:
            log_entry = {
                "email": email,
                "success": success,
                "timestamp": timestamp or datetime.utcnow().isoformat(),
                "ip_address": "unknown",  # 실제로는 요청에서 추출
                "user_agent": "Gateway/1.0"
            }
            self.login_logs.append(log_entry)
            return True
        except Exception as e:
            logger.error(f"로그인 기록 저장 실패: {str(e)}")
            raise Exception(f"로그인 기록 저장 실패: {str(e)}")
    
    async def get_login_history(self, email: str, limit: int = 10) -> List[Dict[str, Any]]:
        """로그인 기록 조회"""
        try:
            user_logs = [log for log in self.login_logs if log["email"] == email]
            return sorted(user_logs, key=lambda x: x["timestamp"], reverse=True)[:limit]
        except Exception as e:
            logger.error(f"로그인 기록 조회 실패: {str(e)}")
            raise Exception(f"로그인 기록 조회 실패: {str(e)}")
    
    async def get_failed_login_count(self, email: str, hours: int = 24) -> int:
        """실패한 로그인 시도 횟수 조회"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            failed_attempts = [
                log for log in self.login_logs 
                if (log["email"] == email and 
                    not log["success"] and 
                    datetime.fromisoformat(log["timestamp"]) > cutoff_time)
            ]
            
            return len(failed_attempts)
        except Exception as e:
            logger.error(f"실패한 로그인 시도 횟수 조회 실패: {str(e)}")
            raise Exception(f"실패한 로그인 시도 횟수 조회 실패: {str(e)}")
    
    async def cleanup_old_logs(self, days: int = 30) -> int:
        """오래된 로그 정리"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            initial_count = len(self.login_logs)
            self.login_logs = [
                log for log in self.login_logs 
                if datetime.fromisoformat(log["timestamp"]) > cutoff_time
            ]
            
            cleaned_count = initial_count - len(self.login_logs)
            logger.info(f"{cleaned_count}개의 오래된 로그가 정리되었습니다")
            
            return cleaned_count
        except Exception as e:
            logger.error(f"로그 정리 실패: {str(e)}")
            raise Exception(f"로그 정리 실패: {str(e)}")
