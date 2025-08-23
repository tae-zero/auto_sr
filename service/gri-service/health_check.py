#!/usr/bin/env python3
"""
GRI Service 헬스체크 스크립트
"""
import requests
import sys
import time

def check_service_health():
    """서비스 헬스체크 수행"""
    try:
        # 서비스 포트
        port = 8006
        url = f"http://localhost:{port}/health"
        
        # 헬스체크 요청
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GRI Service 정상: {data}")
            return True
        else:
            print(f"❌ GRI Service 비정상: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ GRI Service 연결 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ GRI Service 헬스체크 오류: {e}")
        return False

if __name__ == "__main__":
    # 여러 번 시도
    max_retries = 3
    for attempt in range(max_retries):
        if check_service_health():
            sys.exit(0)
        
        if attempt < max_retries - 1:
            print(f"⚠️ 재시도 중... ({attempt + 1}/{max_retries})")
            time.sleep(2)
    
    print("❌ GRI Service 헬스체크 실패")
    sys.exit(1)
