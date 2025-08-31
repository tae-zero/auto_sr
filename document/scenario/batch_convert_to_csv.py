#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
모든 기후 데이터 txt 파일을 일괄적으로 CSV로 변환하는 스크립트
scenario/ 폴더의 모든 txt 파일을 data/ 폴더에 CSV로 저장
"""

import pandas as pd
import os
from pathlib import Path
import glob

def convert_txt_to_csv(input_file_path, output_file_path):
    """기후 데이터 txt 파일을 CSV로 변환 (Year, Sub_Region_Name, Climate_Value)"""
    try:
        print(f"📁 변환 중: {input_file_path.name}")
        
        # 파일 읽기
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 4:
            print(f"⚠️ 파일이 너무 짧습니다: {input_file_path.name}")
            return False
        
        # 1-3행 파싱 (헤더 정보)
        # 1행: "년" + 행정구역 코드들
        # 2행: "년" + 행정구역명들  
        # 3행: "년" + 세부 행정구역명들
        header_line1 = lines[0].strip().split(',')
        header_line2 = lines[1].strip().split(',')
        header_line3 = lines[2].strip().split(',')
        
        # "년" 제거하고 실제 데이터만 추출
        region_codes = header_line1[1:]  # 첫 번째 "년" 제외
        region_names = header_line2[1:]  # 첫 번째 "년" 제외
        sub_region_names = header_line3[1:]  # 첫 번째 "년" 제외
        
        # 데이터 행 파싱 (4행부터)
        data_rows = []
        for line in lines[3:]:
            if line.strip():
                values = line.strip().split(',')
                if len(values) >= len(region_codes) + 1:  # 연도 + 행정구역 수
                    try:
                        year = int(values[0])  # 첫 번째 컬럼은 연도
                        climate_values = values[1:len(region_codes)+1]  # 기후 데이터 값들
                        
                        # 각 행정구역별로 데이터 행 생성 (연도, 세부행정구역명, 기후값)
                        for i, (sub_name, value) in enumerate(zip(sub_region_names, climate_values)):
                            try:
                                climate_value = float(value) if value.strip() else None
                                if climate_value is not None:
                                    data_rows.append({
                                        'Year': year,
                                        'Sub_Region_Name': sub_name,
                                        'Climate_Value': climate_value
                                    })
                            except ValueError:
                                continue
                    except ValueError:
                        continue
        
        if not data_rows:
            print(f"⚠️ 변환할 데이터가 없습니다: {input_file_path.name}")
            return False
        
        # DataFrame 생성 및 CSV 저장
        df = pd.DataFrame(data_rows)
        df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ 변환 완료: {len(data_rows)}행 -> {output_file_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ 변환 실패 {input_file_path.name}: {str(e)}")
        return False

def main():
    """메인 함수: 모든 txt 파일을 일괄 변환"""
    print("🚀 기후 데이터 일괄 CSV 변환 시작...")
    
    # 경로 설정
    scenario_dir = Path(".")
    data_dir = Path("data")
    
    # data 폴더가 없으면 생성
    data_dir.mkdir(exist_ok=True)
    
    # 모든 txt 파일 찾기
    txt_files = list(scenario_dir.rglob("*.txt"))
    
    if not txt_files:
        print("❌ 변환할 txt 파일을 찾을 수 없습니다.")
        return
    
    print(f"📋 발견된 txt 파일: {len(txt_files)}개")
    
    # 변환 통계
    success_count = 0
    fail_count = 0
    
    # 각 txt 파일을 CSV로 변환
    for txt_file in txt_files:
        # 출력 파일명 생성 (txt -> csv)
        output_filename = txt_file.stem + ".csv"
        output_path = data_dir / output_filename
        
        # 변환 실행
        if convert_txt_to_csv(txt_file, output_path):
            success_count += 1
        else:
            fail_count += 1
    
    # 결과 요약
    print("\n" + "="*50)
    print("📊 변환 결과 요약")
    print("="*50)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print(f"📁 저장 위치: {data_dir.absolute()}")
    
    if success_count > 0:
        print(f"\n🎉 {success_count}개의 파일이 성공적으로 CSV로 변환되었습니다!")
        print("data/ 폴더에서 변환된 CSV 파일들을 확인하세요.")

if __name__ == "__main__":
    main()
