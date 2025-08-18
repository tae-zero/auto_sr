from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TCFDInputModel(Base):
    """TCFD 입력 데이터 SQLAlchemy Model"""
    
    __tablename__ = 'tcfd_inputs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    
    # TCFD 11개 인덱스 텍스트 필드
    g1_text = Column(Text, nullable=True)  # 거버넌스 - 이사회 감독
    g2_text = Column(Text, nullable=True)  # 거버넌스 - 경영진 역할
    
    s1_text = Column(Text, nullable=True)  # 전략 - 비즈니스 영향
    s2_text = Column(Text, nullable=True)  # 전략 - 전략적 영향
    s3_text = Column(Text, nullable=True)  # 전략 - 기후 시나리오 분석
    
    r1_text = Column(Text, nullable=True)  # 리스크 관리 - 위험 식별 및 평가
    r2_text = Column(Text, nullable=True)  # 리스크 관리 - 위험 관리 통합
    
    m1_text = Column(Text, nullable=True)  # 지표 및 목표 - 위험 평가 지표
    m2_text = Column(Text, nullable=True)  # 지표 및 목표 - 기회 평가 지표
    m3_text = Column(Text, nullable=True)  # 지표 및 목표 - 목표 설정
    
    # 타임스탬프
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self) -> dict:
        """Model을 딕셔너리로 변환"""
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
