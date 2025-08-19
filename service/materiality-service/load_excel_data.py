#!/usr/bin/env python3
"""
Materiality 엑셀 파일들을 데이터베이스에 로드하는 스크립트
"""

import os
import shutil
import sys
from pathlib import Path

def copy_excel_files():
    """엑셀 파일들을 materiality-service로 복사"""
    
    # 현재 스크립트 위치
    current_dir = Path(__file__).parent
    
    # 소스 엑셀 파일들 위치
    source_dir = Path("../../document/materiality")
    
    # 대상 디렉토리
    target_dir = current_dir / "document" / "materiality"
    
    # 대상 디렉토리 생성
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 엑셀 파일 목록 (서스틴베스트 제외)
    excel_files = [
        "카테고리정리.xlsx",
        "KCGS.xlsx",
        "SASB.xlsx"
    ]
    
    copied_files = []
    
    for filename in excel_files:
        source_path = source_dir / filename
        target_path = target_dir / filename
        
        if source_path.exists():
            try:
                shutil.copy2(source_path, target_path)
                copied_files.append(filename)
                print(f"✅ {filename} 복사 완료")
            except Exception as e:
                print(f"❌ {filename} 복사 실패: {e}")
        else:
            print(f"⚠️ {filename} 파일을 찾을 수 없습니다: {source_path}")
    
    return copied_files

def main():
    """메인 함수"""
    print("🚀 Materiality 엑셀 파일 로드 시작...")
    
    # 1. 엑셀 파일 복사
    print("\n📁 엑셀 파일 복사 중...")
    copied_files = copy_excel_files()
    
    if not copied_files:
        print("❌ 복사할 엑셀 파일이 없습니다.")
        return
    
    print(f"\n✅ {len(copied_files)}개 파일 복사 완료")
    
    # 2. 데이터베이스 로드 안내
    print("\n📊 데이터베이스 로드 방법:")
    print("1. Railway에서 materiality-service 배포")
    print("2. 다음 API 엔드포인트 호출:")
    print("   POST /api/v1/materiality/load-excel-data")
    print("\n또는 직접 스크립트 실행:")
    print("   python -c \"from app.domain.materiality_service import MaterialityService; from app.common.database.database import SessionLocal; db = SessionLocal(); MaterialityService.load_all_excel_files(db)\"")
    
    print("\n🎉 엑셀 파일 준비 완료!")

if __name__ == "__main__":
    main()
