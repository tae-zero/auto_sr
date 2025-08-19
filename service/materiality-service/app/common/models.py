from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
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

class MaterialityAnalysis(Base):
    __tablename__ = "materiality_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    company_name = Column(String)
    analysis_title = Column(String)
    stakeholder_impact = Column(Float)
    business_impact = Column(Float)
    priority_score = Column(Float)
    analysis_content = Column(Text)
    status = Column(String, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 각 엑셀 파일별 테이블 모델
class CategoryTable(Base):
    __tablename__ = "category_table"
    
    id = Column(Integer, primary_key=True, index=True)
    esg_division = Column(String, index=True)  # ESG구분
    materiality_list = Column(String)  # 중대성평가 목록
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class KCGSTable(Base):
    __tablename__ = "kcgs_table"
    
    id = Column(Integer, primary_key=True, index=True)
    environment = Column(String)  # E
    social = Column(String)  # S
    governance = Column(String)  # G
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SASBTable(Base):
    __tablename__ = "sasb_table"
    
    id = Column(Integer, primary_key=True, index=True)
    industry = Column(String, index=True)  # industry
    disclosure_topic = Column(Text)  # Disclosure_Topic
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SustainbestETable(Base):
    __tablename__ = "sustainbest_e_table"
    
    id = Column(Integer, primary_key=True, index=True)
    kpi_category_e = Column(String, index=True)  # KPI_Category_E
    index_name = Column(String)  # index
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SustainbestSTable(Base):
    __tablename__ = "sustainbest_s_table"
    
    id = Column(Integer, primary_key=True, index=True)
    kpi_category_s = Column(String, index=True)  # KPI_Category_S
    index_name = Column(String)  # index
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SustainbestGTable(Base):
    __tablename__ = "sustainbest_g_table"
    
    id = Column(Integer, primary_key=True, index=True)
    kpi_category_g = Column(String, index=True)  # KPI_Category_G
    index_name = Column(String)  # index
    created_at = Column(DateTime(timezone=True), server_default=func.now())
