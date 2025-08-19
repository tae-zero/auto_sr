#!/usr/bin/env python3
"""
Materiality 엑셀 파일들을 각각 별도 테이블로 PostgreSQL 데이터베이스에 업로드하는 스크립트
"""

import pandas as pd
import os
import shutil
from pathlib import Path
import sys

# Railway PostgreSQL 데이터베이스 URL
RAILWAY_DATABASE_URL = "postgresql://postgres:YgIQJWEaQShbuQhRsAdVaeBUZatEgrQO@gondola.proxy.rlwy.net:46735/railway"

# materiality-service 경로를 Python 경로에 추가
sys.path.append('service/materiality-service')

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import List, Dict, Any
import json

# 베이스 클래스 생성
Base = declarative_base()

# 각 엑셀 파일별 테이블 정의
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

def create_tables(engine):
    """데이터베이스 테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 데이터베이스 테이블 생성 완료")
    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")

def save_category_data(db: Session, df: pd.DataFrame) -> int:
    """카테고리정리 데이터를 테이블에 저장"""
    try:
        count = 0
        for index, row in df.iterrows():
            # NaN 값 처리
            esg_division = str(row['ESG구분']) if pd.notna(row['ESG구분']) else ''
            materiality_list = str(row['중대성평가 목록']) if pd.notna(row['중대성평가 목록']) else ''
            
            # 기존 데이터 확인 (중복 방지)
            existing = db.query(CategoryTable).filter(
                CategoryTable.esg_division == esg_division,
                CategoryTable.materiality_list == materiality_list
            ).first()
            
            if not existing:
                category_data = CategoryTable(
                    esg_division=esg_division,
                    materiality_list=materiality_list
                )
                db.add(category_data)
                count += 1
        
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        raise Exception(f"카테고리 데이터 저장 실패: {str(e)}")

def save_kcgs_data(db: Session, df: pd.DataFrame) -> int:
    """KCGS 데이터를 테이블에 저장"""
    try:
        count = 0
        for index, row in df.iterrows():
            # NaN 값 처리
            environment = str(row['E']) if pd.notna(row['E']) else ''
            social = str(row['S']) if pd.notna(row['S']) else ''
            governance = str(row['G']) if pd.notna(row['G']) else ''
            
            # 기존 데이터 확인 (중복 방지)
            existing = db.query(KCGSTable).filter(
                KCGSTable.environment == environment,
                KCGSTable.social == social,
                KCGSTable.governance == governance
            ).first()
            
            if not existing:
                kcgs_data = KCGSTable(
                    environment=environment,
                    social=social,
                    governance=governance
                )
                db.add(kcgs_data)
                count += 1
        
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        raise Exception(f"KCGS 데이터 저장 실패: {str(e)}")

def save_sasb_data(db: Session, df: pd.DataFrame) -> int:
    """SASB 데이터를 테이블에 저장"""
    try:
        count = 0
        for index, row in df.iterrows():
            # NaN 값 처리
            industry = str(row['industry']) if pd.notna(row['industry']) else ''
            disclosure_topic = str(row['Disclosure_Topic']) if pd.notna(row['Disclosure_Topic']) else ''
            
            # 기존 데이터 확인 (중복 방지)
            existing = db.query(SASBTable).filter(
                SASBTable.industry == industry,
                SASBTable.disclosure_topic == disclosure_topic
            ).first()
            
            if not existing:
                sasb_data = SASBTable(
                    industry=industry,
                    disclosure_topic=disclosure_topic
                )
                db.add(sasb_data)
                count += 1
        
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        raise Exception(f"SASB 데이터 저장 실패: {str(e)}")

def save_sustainbest_e_data(db: Session, df: pd.DataFrame) -> int:
    """서스틴베스트 E 데이터를 테이블에 저장"""
    try:
        count = 0
        for index, row in df.iterrows():
            # NaN 값 처리
            kpi_category_e = str(row['KPI_Category_E']) if pd.notna(row['KPI_Category_E']) else ''
            index_name = str(row['index']) if pd.notna(row['index']) else ''
            
            # 기존 데이터 확인 (중복 방지)
            existing = db.query(SustainbestETable).filter(
                SustainbestETable.kpi_category_e == kpi_category_e,
                SustainbestETable.index_name == index_name
            ).first()
            
            if not existing:
                sustainbest_e_data = SustainbestETable(
                    kpi_category_e=kpi_category_e,
                    index_name=index_name
                )
                db.add(sustainbest_e_data)
                count += 1
        
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        raise Exception(f"서스틴베스트 E 데이터 저장 실패: {str(e)}")

def save_sustainbest_s_data(db: Session, df: pd.DataFrame) -> int:
    """서스틴베스트 S 데이터를 테이블에 저장"""
    try:
        count = 0
        for index, row in df.iterrows():
            # NaN 값 처리
            kpi_category_s = str(row['KPI_Category_S']) if pd.notna(row['KPI_Category_S']) else ''
            index_name = str(row['index']) if pd.notna(row['index']) else ''
            
            # 기존 데이터 확인 (중복 방지)
            existing = db.query(SustainbestSTable).filter(
                SustainbestSTable.kpi_category_s == kpi_category_s,
                SustainbestSTable.index_name == index_name
            ).first()
            
            if not existing:
                sustainbest_s_data = SustainbestSTable(
                    kpi_category_s=kpi_category_s,
                    index_name=index_name
                )
                db.add(sustainbest_s_data)
                count += 1
        
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        raise Exception(f"서스틴베스트 S 데이터 저장 실패: {str(e)}")

def save_sustainbest_g_data(db: Session, df: pd.DataFrame) -> int:
    """서스틴베스트 G 데이터를 테이블에 저장"""
    try:
        count = 0
        for index, row in df.iterrows():
            # NaN 값 처리
            kpi_category_g = str(row['KPI_Category_G']) if pd.notna(row['KPI_Category_G']) else ''
            index_name = str(row['index']) if pd.notna(row['index']) else ''
            
            # 기존 데이터 확인 (중복 방지)
            existing = db.query(SustainbestGTable).filter(
                SustainbestGTable.kpi_category_g == kpi_category_g,
                SustainbestGTable.index_name == index_name
            ).first()
            
            if not existing:
                sustainbest_g_data = SustainbestGTable(
                    kpi_category_g=kpi_category_g,
                    index_name=index_name
                )
                db.add(sustainbest_g_data)
                count += 1
        
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        raise Exception(f"서스틴베스트 G 데이터 저장 실패: {str(e)}")

def upload_excel_to_database():
    """엑셀 파일들을 각각 별도 테이블로 데이터베이스에 업로드"""
    
    print("🚀 Materiality 엑셀 파일들을 각각 별도 테이블로 업로드 시작...")
    
    # Railway 데이터베이스 연결
    try:
        engine = create_engine(RAILWAY_DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        print("✅ Railway 데이터베이스 연결 성공")
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return
    
    # 테이블 생성
    create_tables(engine)
    
    # 소스 디렉토리
    source_dir = Path("document/materiality")
    
    total_uploaded = 0
    
    # 1. 카테고리정리.xlsx -> category_table
    category_file = source_dir / "카테고리정리.xlsx"
    if category_file.exists():
        try:
            print(f"\n📊 카테고리정리.xlsx 처리 중...")
            df = pd.read_excel(category_file)
            print(f"   📋 컬럼: {list(df.columns)}")
            print(f"   📊 행 수: {len(df)}")
            
            count = save_category_data(db, df)
            total_uploaded += count
            print(f"✅ category_table: {count}개 데이터 저장 완료")
            
        except Exception as e:
            print(f"❌ 카테고리정리 처리 실패: {e}")
    else:
        print(f"⚠️ 카테고리정리.xlsx 파일을 찾을 수 없습니다")
    
    # 2. KCGS.xlsx -> kcgs_table
    kcgs_file = source_dir / "KCGS.xlsx"
    if kcgs_file.exists():
        try:
            print(f"\n📊 KCGS.xlsx 처리 중...")
            df = pd.read_excel(kcgs_file)
            print(f"   📋 컬럼: {list(df.columns)}")
            print(f"   📊 행 수: {len(df)}")
            
            count = save_kcgs_data(db, df)
            total_uploaded += count
            print(f"✅ kcgs_table: {count}개 데이터 저장 완료")
            
        except Exception as e:
            print(f"❌ KCGS 처리 실패: {e}")
    else:
        print(f"⚠️ KCGS.xlsx 파일을 찾을 수 없습니다")
    
    # 3. SASB.xlsx -> sasb_table
    sasb_file = source_dir / "SASB.xlsx"
    if sasb_file.exists():
        try:
            print(f"\n📊 SASB.xlsx 처리 중...")
            df = pd.read_excel(sasb_file)
            print(f"   📋 컬럼: {list(df.columns)}")
            print(f"   📊 행 수: {len(df)}")
            
            count = save_sasb_data(db, df)
            total_uploaded += count
            print(f"✅ sasb_table: {count}개 데이터 저장 완료")
            
        except Exception as e:
            print(f"❌ SASB 처리 실패: {e}")
    else:
        print(f"⚠️ SASB.xlsx 파일을 찾을 수 없습니다")
    
    # 4. 서스틴베스트_E.xlsx -> sustainbest_e_table
    sustainbest_e_file = source_dir / "서스틴베스트_E.xlsx"
    if sustainbest_e_file.exists():
        try:
            print(f"\n📊 서스틴베스트_E.xlsx 처리 중...")
            df = pd.read_excel(sustainbest_e_file)
            print(f"   📋 컬럼: {list(df.columns)}")
            print(f"   📊 행 수: {len(df)}")
            
            count = save_sustainbest_e_data(db, df)
            total_uploaded += count
            print(f"✅ sustainbest_e_table: {count}개 데이터 저장 완료")
            
        except Exception as e:
            print(f"❌ 서스틴베스트_E 처리 실패: {e}")
    else:
        print(f"⚠️ 서스틴베스트_E.xlsx 파일을 찾을 수 없습니다")
    
    # 5. 서스틴베스트_S.xlsx -> sustainbest_s_table
    sustainbest_s_file = source_dir / "서스틴베스트_S.xlsx"
    if sustainbest_s_file.exists():
        try:
            print(f"\n📊 서스틴베스트_S.xlsx 처리 중...")
            df = pd.read_excel(sustainbest_s_file)
            print(f"   📋 컬럼: {list(df.columns)}")
            print(f"   📊 행 수: {len(df)}")
            
            count = save_sustainbest_s_data(db, df)
            total_uploaded += count
            print(f"✅ sustainbest_s_table: {count}개 데이터 저장 완료")
            
        except Exception as e:
            print(f"❌ 서스틴베스트_S 처리 실패: {e}")
    else:
        print(f"⚠️ 서스틴베스트_S.xlsx 파일을 찾을 수 없습니다")
    
    # 6. 서스틴베스트_G.xlsx -> sustainbest_g_table
    sustainbest_g_file = source_dir / "서스틴베스트_G.xlsx"
    if sustainbest_g_file.exists():
        try:
            print(f"\n📊 서스틴베스트_G.xlsx 처리 중...")
            df = pd.read_excel(sustainbest_g_file)
            print(f"   📋 컬럼: {list(df.columns)}")
            print(f"   📊 행 수: {len(df)}")
            
            count = save_sustainbest_g_data(db, df)
            total_uploaded += count
            print(f"✅ sustainbest_g_table: {count}개 데이터 저장 완료")
            
        except Exception as e:
            print(f"❌ 서스틴베스트_G 처리 실패: {e}")
    else:
        print(f"⚠️ 서스틴베스트_G.xlsx 파일을 찾을 수 없습니다")
    
    db.close()
    
    print(f"\n🎉 업로드 완료! 총 {total_uploaded}개 데이터가 6개 테이블에 저장되었습니다.")
    print("📊 생성된 테이블:")
    print("   - category_table (카테고리정리)")
    print("   - kcgs_table (KCGS)")
    print("   - sasb_table (SASB)")
    print("   - sustainbest_e_table (서스틴베스트_E)")
    print("   - sustainbest_s_table (서스틴베스트_S)")
    print("   - sustainbest_g_table (서스틴베스트_G)")

if __name__ == "__main__":
    upload_excel_to_database()
