from datetime import datetime
from typing import Optional

class TCFDDraftEntity:
    """TCFD 초안 데이터 Entity"""
    
    def __init__(
        self,
        company_name: str,
        user_id: Optional[str] = None,
        tcfd_input_id: Optional[int] = None,
        draft_content: Optional[str] = None,
        draft_type: Optional[str] = None,
        file_path: Optional[str] = None,
        status: str = "processing",
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.company_name = company_name
        self.user_id = user_id
        self.tcfd_input_id = tcfd_input_id
        self.draft_content = draft_content
        self.draft_type = draft_type
        self.file_path = file_path
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> dict:
        """Entity를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "company_name": self.company_name,
            "user_id": self.user_id,
            "tcfd_input_id": self.tcfd_input_id,
            "draft_content": self.draft_content,
            "draft_type": self.draft_type,
            "file_path": self.file_path,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TCFDDraftEntity':
        """딕셔너리에서 Entity 생성"""
        return cls(
            id=data.get('id'),
            company_name=data.get('company_name'),
            user_id=data.get('user_id'),
            tcfd_input_id=data.get('tcfd_input_id'),
            draft_content=data.get('draft_content'),
            draft_type=data.get('draft_type'),
            file_path=data.get('file_path'),
            status=data.get('status', 'processing'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
