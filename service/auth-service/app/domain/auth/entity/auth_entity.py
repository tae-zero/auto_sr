"""
Auth Service Auth 엔티티
- 인증 데이터베이스 엔티티
- 사용자 인증 정보 및 세션
"""
from typing import Optional
from datetime import datetime
import uuid

class AuthEntity:
    """인증 데이터베이스 엔티티"""
    
    def __init__(
        self,
        user_id: Optional[str] = None,
        email: str = "",
        company_id: str = "",
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.user_id = user_id or str(uuid.uuid4())
        self.email = email
        self.company_id = company_id
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            'user_id': self.user_id,
            'email': self.email,
            'company_id': self.company_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AuthEntity':
        """딕셔너리에서 엔티티 생성"""
        return cls(
            user_id=data.get('user_id'),
            email=data.get('email', ''),
            company_id=data.get('company_id', ''),
            status=data.get('status', 'active'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def update_status(self, new_status: str) -> None:
        """상태 업데이트"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """활성 상태 확인"""
        return self.status == "active"
    
    def is_suspended(self) -> bool:
        """정지 상태 확인"""
        return self.status == "suspended"
    
    def is_deleted(self) -> bool:
        """삭제 상태 확인"""
        return self.status == "deleted"
    
    def __repr__(self) -> str:
        return f"AuthEntity(user_id='{self.user_id}', email='{self.email}', status='{self.status}')"

class UserEntity:
    """사용자 세션 엔티티"""
    
    def __init__(
        self,
        auth_id: str = "",
        email: str = "",
        status: str = "active",
        created_at: Optional[datetime] = None
    ):
        self.auth_id = auth_id
        self.email = email
        self.status = status
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            'auth_id': self.auth_id,
            'email': self.email,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserEntity':
        """딕셔너리에서 엔티티 생성"""
        return cls(
            auth_id=data.get('auth_id', ''),
            email=data.get('email', ''),
            status=data.get('status', 'active'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )
    
    def is_active(self) -> bool:
        """활성 상태 확인"""
        return self.status == "active"
    
    def __repr__(self) -> str:
        return f"UserEntity(auth_id='{self.auth_id}', email='{self.email}', status='{self.status}')"
