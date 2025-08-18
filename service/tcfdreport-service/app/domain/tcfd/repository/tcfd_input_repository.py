from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..model.tcfd_input_model import TCFDInputModel
from ..entity.tcfd_input_entity import TCFDInputEntity

class TCFDInputRepository:
    """TCFD 입력 데이터 Repository"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def save(self, tcfd_input: TCFDInputEntity) -> int:
        """TCFD 입력 데이터 저장"""
        model = TCFDInputModel(
            company_name=tcfd_input.company_name,
            user_id=tcfd_input.user_id,
            g1_text=tcfd_input.g1_text,
            g2_text=tcfd_input.g2_text,
            s1_text=tcfd_input.s1_text,
            s2_text=tcfd_input.s2_text,
            s3_text=tcfd_input.s3_text,
            r1_text=tcfd_input.r1_text,
            r2_text=tcfd_input.r2_text,
            m1_text=tcfd_input.m1_text,
            m2_text=tcfd_input.m2_text,
            m3_text=tcfd_input.m3_text
        )
        
        self.db_session.add(model)
        self.db_session.commit()
        self.db_session.refresh(model)
        
        return model.id
    
    def find_by_id(self, input_id: int) -> Optional[TCFDInputEntity]:
        """ID로 TCFD 입력 데이터 조회"""
        model = self.db_session.query(TCFDInputModel).filter(
            TCFDInputModel.id == input_id
        ).first()
        
        if not model:
            return None
        
        return TCFDInputEntity(
            id=model.id,
            company_name=model.company_name,
            user_id=model.user_id,
            g1_text=model.g1_text,
            g2_text=model.g2_text,
            s1_text=model.s1_text,
            s2_text=model.s2_text,
            s3_text=model.s3_text,
            r1_text=model.r1_text,
            r2_text=model.r2_text,
            m1_text=model.m1_text,
            m2_text=model.m2_text,
            m3_text=model.m3_text,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def find_by_company(self, company_name: str) -> List[TCFDInputEntity]:
        """회사명으로 TCFD 입력 데이터 조회"""
        models = self.db_session.query(TCFDInputModel).filter(
            TCFDInputModel.company_name == company_name
        ).order_by(TCFDInputModel.created_at.desc()).all()
        
        entities = []
        for model in models:
            entity = TCFDInputEntity(
                id=model.id,
                company_name=model.company_name,
                user_id=model.user_id,
                g1_text=model.g1_text,
                g2_text=model.g2_text,
                s1_text=model.s1_text,
                s2_text=model.s2_text,
                s3_text=model.s3_text,
                r1_text=model.r1_text,
                r2_text=model.r2_text,
                m1_text=model.m1_text,
                m2_text=model.m2_text,
                m3_text=model.m3_text,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
            entities.append(entity)
        
        return entities
    
    def find_by_user(self, user_id: str) -> List[TCFDInputEntity]:
        """사용자 ID로 TCFD 입력 데이터 조회"""
        models = self.db_session.query(TCFDInputModel).filter(
            TCFDInputModel.user_id == user_id
        ).order_by(TCFDInputModel.created_at.desc()).all()
        
        entities = []
        for model in models:
            entity = TCFDInputEntity(
                id=model.id,
                company_name=model.company_name,
                user_id=model.user_id,
                g1_text=model.g1_text,
                g2_text=model.g2_text,
                s1_text=model.s1_text,
                s2_text=model.s2_text,
                s3_text=model.s3_text,
                r1_text=model.r1_text,
                r2_text=model.r2_text,
                m1_text=model.m1_text,
                m2_text=model.m2_text,
                m3_text=model.m3_text,
                created_at=model.created_at,
                updated_at=model.updated_at
            )
            entities.append(entity)
        
        return entities
    
    def update(self, input_id: int, tcfd_input: TCFDInputEntity) -> bool:
        """TCFD 입력 데이터 업데이트"""
        model = self.db_session.query(TCFDInputModel).filter(
            TCFDInputModel.id == input_id
        ).first()
        
        if not model:
            return False
        
        # 업데이트할 필드들
        model.g1_text = tcfd_input.g1_text
        model.g2_text = tcfd_input.g2_text
        model.s1_text = tcfd_input.s1_text
        model.s2_text = tcfd_input.s2_text
        model.s3_text = tcfd_input.s3_text
        model.r1_text = tcfd_input.r1_text
        model.r2_text = tcfd_input.r2_text
        model.m1_text = tcfd_input.m1_text
        model.m2_text = tcfd_input.m2_text
        model.m3_text = tcfd_input.m3_text
        
        self.db_session.commit()
        return True
    
    def delete(self, input_id: int) -> bool:
        """TCFD 입력 데이터 삭제"""
        model = self.db_session.query(TCFDInputModel).filter(
            TCFDInputModel.id == input_id
        ).first()
        
        if not model:
            return False
        
        self.db_session.delete(model)
        self.db_session.commit()
        return True
