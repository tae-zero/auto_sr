#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기후 데이터 텍스트 파일을 CSV 형식으로 변환하는 스크립트
AR6_SSP126_5ENSMN_skorea_RAIN80_sgg261_yearly_2021_2100.txt 파일을 CSV로 변환
"""

import pandas as pd
import os
from pathlib import Path

def convert_climate_data_to_csv(input_file_path, output_file_path):
    """
    기후 데이터 텍스트 파일을 CSV 형식으로 변환
    
    Args:
        input_file_path (str): 입력 텍스트 파일 경로
        output_file_path (str): 출력 CSV 파일 경로
    """
    try:
        print(f"📁 입력 파일: {input_file_path}")
        print(f"📁 출력 파일: {output_file_path}")
        
        # 파일 읽기
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 4:
            raise ValueError("파일이 너무 짧습니다. 최소 4행이 필요합니다.")
        
        # 1-3행 파싱 (헤더 정보)
        region_codes = lines[0].strip().split(',')  # 행정구역 코드
        region_names = lines[1].strip().split(',')  # 행정구역명
        sub_region_names = lines[2].strip().split(',')  # 세부 행정구역명
        
        print(f"✅ 행정구역 수: {len(region_codes)}")
        print(f"✅ 데이터 연도 범위: 2021-2100")
        
        # 데이터 행 파싱 (4행부터)
        data_rows = []
        for line in lines[3:]:
            if line.strip():
                values = line.strip().split(',')
                if len(values) >= len(region_codes):
                    year = int(values[0])  # 첫 번째 컬럼은 연도
                    climate_values = values[1:len(region_codes)+1]  # 기후 데이터 값들
                    
                    # 각 행정구역별로 데이터 행 생성
                    for i, (code, name, sub_name, value) in enumerate(zip(region_codes, region_names, sub_region_names, climate_values)):
                        try:
                            climate_value = float(value) if value.strip() else None
                            data_rows.append({
                                'Year': year,
                                'Region_Code': code,
                                'Region_Name': name,
                                'Sub_Region_Name': sub_name,
                                'Climate_Value': climate_value
                            })
                        except ValueError:
                            # 값이 숫자가 아닌 경우 None으로 설정
                            data_rows.append({
                                'Year': year,
                                'Region_Code': code,
                                'Region_Name': name,
                                'Sub_Region_Name': sub_name,
                                'Climate_Value': None
                            })
        
        # DataFrame 생성
        df = pd.DataFrame(data_rows)
        
        print(f"✅ 변환된 데이터: {len(df)} 행")
        print(f"✅ 컬럼: {list(df.columns)}")
        
        # CSV 파일로 저장
        df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ CSV 파일 저장 완료: {output_file_path}")
        
        # 데이터 미리보기
        print("\n📊 데이터 미리보기:")
        print(df.head(10))
        
        # 기본 통계
        print(f"\n📈 기본 통계:")
        print(f"연도 범위: {df['Year'].min()} - {df['Year'].max()}")
        print(f"행정구역 수: {df['Region_Code'].nunique()}")
        print(f"유효한 기후 데이터: {df['Climate_Value'].notna().sum()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 변환 실패: {str(e)}")
        return False

def main():
    """메인 함수"""
    # 현재 디렉토리에서 입력 파일 찾기
    current_dir = Path(".")
    
    # 입력 파일명
    input_filename = "AR6_SSP126_5ENSMN_skorea_RAIN80_sgg261_yearly_2021_2100.txt"
    
    # 입력 파일 경로
    input_file_path = current_dir / input_filename
    
    if not input_file_path.exists():
        print(f"❌ 입력 파일을 찾을 수 없습니다: {input_file_path}")
        print("현재 디렉토리의 파일들:")
        for file in current_dir.glob("*.txt"):
            print(f"  - {file.name}")
        return
    
    # 출력 파일 경로
    output_filename = input_filename.replace('.txt', '.csv')
    output_file_path = current_dir / output_filename
    
    print("🔄 기후 데이터 텍스트 파일을 CSV로 변환 시작...")
    print("=" * 60)
    
    # 변환 실행
    success = convert_climate_data_to_csv(input_file_path, output_file_path)
    
    if success:
        print("\n🎉 변환 완료!")
        print(f"📁 CSV 파일: {output_file_path}")
        print(f"📊 파일 크기: {output_file_path.stat().st_size / 1024:.1f} KB")
    else:
        print("\n❌ 변환 실패!")

if __name__ == "__main__":
    main()
