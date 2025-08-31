#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기후 데이터 API 통합 테스트 스크립트
TCFD Service -> Gateway -> Frontend 연결 테스트
"""

import requests
import json
import base64
from io import BytesIO

def test_climate_api():
    """기후 데이터 API 테스트"""
    
    # TCFD Service 직접 테스트 (Railway)
    print("🚀 1. TCFD Service 직접 테스트 (Railway)")
    print("=" * 50)
    
    tcfd_service_url = "https://tcfd-service-production-0b8c.up.railway.app"
    
    try:
        # 1. 기후 시나리오 데이터 조회
        print("📊 기후 시나리오 데이터 조회 테스트...")
        response = requests.get(
            f"{tcfd_service_url}/api/v1/tcfd/climate-scenarios",
            params={
                "scenario_code": "SSP126",
                "variable_code": "HW33",
                "year": 2021
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공: {data.get('message', '데이터 조회 완료')}")
            print(f"📈 데이터 수: {len(data.get('data', []))}")
        else:
            print(f"❌ 실패: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ TCFD Service 연결 실패: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # Gateway 테스트 (로컬)
    print("🚀 2. Gateway 테스트 (로컬)")
    print("=" * 50)
    
    gateway_url = "http://localhost:8000"
    
    try:
        # 1. 기후 시나리오 데이터 조회
        print("📊 기후 시나리오 데이터 조회 테스트...")
        response = requests.get(
            f"{gateway_url}/api/v1/tcfd/climate-scenarios",
            params={
                "scenario_code": "SSP126",
                "variable_code": "HW33",
                "year": 2021
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공: {data.get('message', '데이터 조회 완료')}")
            print(f"📈 데이터 수: {len(data.get('data', []))}")
        else:
            print(f"❌ 실패: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Gateway 연결 실패: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # 테이블 이미지 생성 테스트
    print("🚀 3. 테이블 이미지 생성 테스트")
    print("=" * 50)
    
    try:
        print("🖼️ 테이블 이미지 생성 테스트...")
        response = requests.get(
            f"{tcfd_service_url}/api/v1/tcfd/climate-scenarios/table-image",
            params={
                "scenario_code": "SSP126",
                "variable_code": "HW33",
                "start_year": 2021,
                "end_year": 2030
            },
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공: {data.get('message', '이미지 생성 완료')}")
            
            # base64 이미지 데이터 확인
            image_data = data.get('image_data', '')
            if image_data and image_data.startswith('data:image'):
                print("✅ 이미지 데이터 생성 성공")
                
                # 이미지 파일로 저장
                try:
                    # base64 데이터에서 실제 이미지 데이터 추출
                    if ',' in image_data:
                        image_base64 = image_data.split(',')[1]
                    else:
                        image_base64 = image_data
                    
                    image_bytes = base64.b64decode(image_base64)
                    
                    # 이미지 파일로 저장
                    with open('test_climate_table.png', 'wb') as f:
                        f.write(image_bytes)
                    print("💾 이미지 파일 저장 완료: test_climate_table.png")
                    
                except Exception as e:
                    print(f"❌ 이미지 저장 실패: {str(e)}")
            else:
                print("❌ 이미지 데이터가 올바르지 않습니다")
        else:
            print(f"❌ 실패: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ 테이블 이미지 생성 실패: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 테스트 완료!")

if __name__ == "__main__":
    test_climate_api()
