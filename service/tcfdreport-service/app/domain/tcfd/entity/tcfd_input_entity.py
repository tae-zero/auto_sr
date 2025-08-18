from datetime import datetime
from typing import Optional

class TCFDInputEntity:
    """TCFD 입력 데이터 Entity"""
    
    def __init__(
        self,
        company_name: str,
        user_id: Optional[str] = None,
        g1_text: Optional[str] = None,
        g2_text: Optional[str] = None,
        s1_text: Optional[str] = None,
        s2_text: Optional[str] = None,
        s3_text: Optional[str] = None,
        r1_text: Optional[str] = None,
        r2_text: Optional[str] = None,
        m1_text: Optional[str] = None,
        m2_text: Optional[str] = None,
        m3_text: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.company_name = company_name
        self.user_id = user_id
        self.g1_text = g1_text
        self.g2_text = g2_text
        self.s1_text = s1_text
        self.s2_text = s2_text
        self.s3_text = s3_text
        self.r1_text = r1_text
        self.r2_text = r2_text
        self.m1_text = m1_text
        self.m2_text = m2_text
        self.m3_text = m3_text
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> dict:
        """Entity를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'user_id': self.user_id,
            'g1_text': self.g1_text,
            'g2_text': self.g2_text,
            's1_text': self.s1_text,
            's2_text': self.s2_text,
            's3_text': self.s3_text,
            'r1_text': self.r1_text,
            'r2_text': self.r2_text,
            'm1_text': self.m1_text,
            'm2_text': self.m2_text,
            'm3_text': self.m3_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TCFDInputEntity':
        """딕셔너리에서 Entity 생성"""
        return cls(
            id=data.get('id'),
            company_name=data['company_name'],
            user_id=data.get('user_id'),
            g1_text=data.get('g1_text'),
            g2_text=data.get('g2_text'),
            s1_text=data.get('s1_text'),
            s2_text=data.get('s2_text'),
            s3_text=data.get('s3_text'),
            r1_text=data.get('r1_text'),
            r2_text=data.get('r2_text'),
            m1_text=data.get('m1_text'),
            m2_text=data.get('m2_text'),
            m3_text=data.get('m3_text'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
