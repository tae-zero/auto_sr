#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기후 데이터 텍스트 파일을 간단한 CSV 형식으로 변환하는 스크립트
Year, Sub_Region_Name, Climate_Value 컬럼 포함
"""

import pandas as pd
from pathlib import Path

def convert_to_simple_csv(input_file_path, output_file_path):
    """기후 데이터를 간단한 CSV로 변환 (Year, Sub_Region_Name, Climate_Value)"""
    try:
        print(f"📁 입력 파일: {input_file_path}")
        print(f"📁 출력 파일: {output_file_path}")
        
        # 파일 읽기
        with open(input_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) < 4:
            raise ValueError("파일이 너무 짧습니다.")
        
        # 1-3행 파싱 (헤더 정보)
        # 1행: "년" + 행정구역 코드들
        # 2행: "년" + 행정구역명들  
        # 3행: "년" + 세부 행정구역명들
        header_line = lines[0].strip().split(',')
        region_names_line = lines[1].strip().split(',')
        sub_region_names_line = lines[2].strip().split(',')
        
        # 첫 번째 컬럼은 "년"이므로 제외하고 실제 데이터 컬럼들만 추출
        region_codes = header_line[1:]  # 행정구역 코드들
        region_names = region_names_line[1:]  # 행정구역명들
        sub_region_names = sub_region_names_line[1:]  # 세부 행정구역명들
        
        print(f"✅ 행정구역 수: {len(region_codes)}")
        print(f"✅ 데이터 연도 범위: 2021-2100")
        
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
                                # 값이 숫자가 아니면 건너뛰기
                                continue
                    except (ValueError, IndexError):
                        # 연도 변환 실패 시 해당 행 건너뛰기
                        continue
        
        if not data_rows:
            raise ValueError("파싱된 데이터가 없습니다.")
        
        # DataFrame 생성
        df = pd.DataFrame(data_rows)
        
        print(f"✅ 변환된 데이터: {len(df)} 행")
        print(f"✅ 컬럼: {list(df.columns)}")
        
        # CSV 파일 저장
        df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
        print(f"✅ CSV 파일 저장 완료: {output_file_path}")
        
        # 데이터 미리보기
        print(f"\n📊 데이터 미리보기:")
        print(df.head())
        
        # 기본 통계
        print(f"\n📈 기본 통계:")
        print(f"연도 범위: {df['Year'].min()} ~ {df['Year'].max()}")
        print(f"행정구역 수: {df['Sub_Region_Name'].nunique()}")
        print(f"기후값 범위: {df['Climate_Value'].min():.2f} ~ {df['Climate_Value'].max():.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 변환 실패: {str(e)}")
        return False

def main():
    """메인 함수"""
    print("🔄 기후 데이터를 간단한 CSV로 변환 시작...")
    print("=" * 50)
    
    # 파일 경로 설정
    input_file = "AR6_SSP126_5ENSMN_skorea_RAIN80_sgg261_yearly_2021_2100.txt"
    output_file = "climate_data_simple.csv"
    
    # 변환 실행
    success = convert_to_simple_csv(input_file, output_file)
    
    if success:
        print("\n🎉 변환 완료!")
    else:
        print("\n❌ 변환 실패!")

if __name__ == "__main__":
    main()
