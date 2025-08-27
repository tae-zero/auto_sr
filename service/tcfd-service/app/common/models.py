from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.common.database.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    auth_id = Column(String, unique=True, index=True)
    auth_pw = Column(String)
    name = Column(String)
    age = Column(String)
    company_id = Column(String)
    industry = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TCFDStandard(Base):
    __tablename__ = "tcfd_standard"
    # id 컬럼 제거 (실제 DB에 없음)
    category = Column(String, primary_key=True, index=True)
    disclosure_id = Column(String, primary_key=True, index=True)
    disclosure_summary = Column(Text)
    disclosure_detail = Column(Text)

class TCFDInput(Base):
    __tablename__ = "tcfd_inputs"
    id = Column(Integer, primary_key=True, index=True)
    governance_g1 = Column(Text)
    governance_g2 = Column(Text)
    strategy_s1 = Column(Text)
    strategy_s2 = Column(Text)
    strategy_s3 = Column(Text)
    risk_management_r1 = Column(Text)
    risk_management_r2 = Column(Text)
    risk_management_r3 = Column(Text)
    metrics_targets_m1 = Column(Text)
    metrics_targets_m2 = Column(Text)
    metrics_targets_m3 = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
