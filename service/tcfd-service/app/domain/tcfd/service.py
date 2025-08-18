from sqlalchemy.orm import Session
from app.common.models import User, TCFDStandard
from app.domain.tcfd.tcfd_schema import TCFDStandardResponse
from typing import List, Optional

class TCFDService:
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    def get_tcfd_standards(self, db: Session) -> List[TCFDStandard]:
        """TCFD 표준 정보 전체 조회"""
        return db.query(TCFDStandard).all()
    
    def get_tcfd_standards_by_category(self, db: Session, category: str) -> List[TCFDStandard]:
        """카테고리별 TCFD 표준 정보 조회"""
        return db.query(TCFDStandard).filter(TCFDStandard.category == category).all()
