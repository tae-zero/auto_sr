#!/usr/bin/env python3
"""
기후 데이터 압축파일 해제 스크립트
plis_126과 plis_585 폴더의 tar.gz 파일들을 document/scenario 폴더에 해제
"""

import tarfile
import os
import shutil
from pathlib import Path

def extract_climate_data():
    """기후 데이터 압축파일 해제"""
    
    # 기본 경로 설정 - document/scenario 폴더로 변경
    base_path = Path("document/scenario")
    plis_126_path = Path("Scenario/plis_126")
    plis_585_path = Path("Scenario/plis_585")
    
    # document/scenario 폴더가 없으면 생성
    base_path.mkdir(parents=True, exist_ok=True)
    
    print("🗜️ 기후 데이터 압축파일 해제 시작...")
    print(f"📁 저장 위치: {base_path.absolute()}")
    
    # plis_126 폴더 처리
    if plis_126_path.exists():
        print(f"📁 {plis_126_path} 폴더 처리 중...")
        extract_folder(plis_126_path, base_path, "SSP126")
    
    # plis_585 폴더 처리
    if plis_585_path.exists():
        print(f"📁 {plis_585_path} 폴더 처리 중...")
        extract_folder(plis_585_path, base_path, "SSP585")
    
    print("✅ 모든 압축파일 해제 완료!")

def extract_folder(folder_path: Path, base_path: Path, scenario_name: str):
    """특정 폴더의 모든 tar.gz 파일 해제"""
    
    # 폴더 내 모든 tar.gz 파일 찾기
    tar_files = list(folder_path.glob("*.tar.gz"))
    
    if not tar_files:
        print(f"⚠️ {folder_path}에 tar.gz 파일이 없습니다.")
        return
    
    print(f"🔍 {len(tar_files)}개의 tar.gz 파일 발견")
    
    for tar_file in tar_files:
        try:
            print(f"📦 {tar_file.name} 해제 중...")
            
            # 압축 해제
            with tarfile.open(tar_file, 'r:gz') as tar:
                # 파일명에서 정보 추출
                file_info = extract_file_info(tar_file.name)
                
                # 해제할 폴더명 생성
                extract_folder_name = f"{scenario_name}_{file_info['variable']}_{file_info['period']}"
                extract_path = base_path / extract_folder_name
                
                # 기존 폴더가 있으면 삭제
                if extract_path.exists():
                    shutil.rmtree(extract_path)
                
                # 압축 해제
                tar.extractall(path=extract_path)
                
                # ASC 파일 확인
                asc_files = list(extract_path.glob("*.asc"))
                if asc_files:
                    print(f"  ✅ {len(asc_files)}개 ASC 파일 해제 완료")
                else:
                    print(f"  ⚠️ ASC 파일을 찾을 수 없습니다")
                
        except Exception as e:
            print(f"  ❌ {tar_file.name} 해제 실패: {e}")

def extract_file_info(filename: str) -> dict:
    """파일명에서 정보 추출"""
    # AR6_SSP126_5ENSMN_skorea_RN_sgg261_yearly_2021_2100_asc.tar.gz
    parts = filename.split('_')
    
    return {
        'scenario': parts[1],      # SSP126 or SSP585
        'variable': parts[4],      # RN, RAIN80, HW33, TR25, TA
        'region': parts[3],        # skorea
        'period': f"{parts[6]}_{parts[7]}"  # 2021_2100
    }

def create_summary():
    """해제된 파일들의 요약 정보 생성"""
    
    base_path = Path("document/scenario")
    
    print("\n📋 해제된 파일 요약:")
    print("=" * 50)
    
    # document/scenario 폴더 내 모든 폴더 검사
    for folder in base_path.iterdir():
        if folder.is_dir() and not folder.name.startswith('.'):
            print(f"📁 {folder.name}")
            
            # 폴더 내 파일들 확인
            files = list(folder.glob("*"))
            for file in files:
                if file.is_file():
                    size = file.stat().st_size
                    print(f"  📄 {file.name} ({size:,} bytes)")
            print()

if __name__ == "__main__":
    try:
        # 압축 해제 실행
        extract_climate_data()
        
        # 요약 정보 생성
        create_summary()
        
        print("🎉 모든 작업이 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
