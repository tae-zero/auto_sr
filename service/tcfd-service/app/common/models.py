from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.common.database.database import Base
from datetime import datetime

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

# 기후 시나리오 관련 테이블들
class ClimateScenario(Base):
    __tablename__ = "climate_scenarios"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_code = Column(String(20), unique=True, index=True, nullable=False)  # SSP126, SSP585
    scenario_name = Column(String(100), nullable=False)  # SSP1-2.6, SSP5-8.5
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClimateVariable(Base):
    __tablename__ = "climate_variables"
    
    id = Column(Integer, primary_key=True, index=True)
    variable_code = Column(String(20), unique=True, index=True, nullable=False)  # HW33, RN, TA, TR25, RAIN80
    variable_name = Column(String(100), nullable=False)  # 폭염일수, 연강수량, 연평균기온, 열대야일수, 호우일수
    unit = Column(String(50), nullable=False)  # 일, mm, °C, 일, 일
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AdministrativeRegion(Base):
    __tablename__ = "administrative_regions"
    
    id = Column(Integer, primary_key=True, index=True)
    region_code = Column(String(20), unique=True, index=True, nullable=False)  # sgg261
    region_name = Column(String(100), nullable=False)  # 행정구역명
    parent_region = Column(String(100))  # 상위 행정구역
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClimateData(Base):
    __tablename__ = "climate_data"
    
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(Integer, ForeignKey("climate_scenarios.id"), nullable=False)
    variable_id = Column(Integer, ForeignKey("climate_variables.id"), nullable=False)
    region_id = Column(Integer, ForeignKey("administrative_regions.id"), nullable=False)
    year = Column(Integer, nullable=False)  # 연도 (2021-2100)
    value = Column(Float, nullable=False)  # 기후값
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    scenario = relationship("ClimateScenario", backref="climate_data")
    variable = relationship("ClimateVariable", backref="climate_data")
    region = relationship("AdministrativeRegion", backref="climate_data")
    
    # 복합 인덱스
    __table_args__ = (
        Index('idx_climate_data_lookup', 'scenario_id', 'variable_id', 'region_id', 'year'),
    )
