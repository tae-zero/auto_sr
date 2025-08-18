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
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    disclosure_id = Column(String)
    disclosure_summary = Column(Text)
    disclosure_detail = Column(Text)
