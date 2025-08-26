#!/usr/bin/env python3
"""
LLM Service API 테스트 스크립트
"""

import requests
import json
import time
from typing import Dict, Any

# 서비스 URL (로컬 테스트용)
BASE_URL = "http://localhost:8002"

def test_health():
    """헬스체크 테스트"""
    print("🔍 헬스체크 테스트...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 헬스체크 실패: {e}")
        return False

def test_root():
    """루트 엔드포인트 테스트"""
    print("\n🔍 루트 엔드포인트 테스트...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 루트 엔드포인트 테스트 실패: {e}")
        return False

def test_search():
    """검색 API 테스트"""
    print("\n🔍 검색 API 테스트...")
    try:
        payload = {
            "question": "한온시스템 TCFD 전략 핵심을 요약해줘",
            "top_k": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/rag/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"검색 결과 수: {len(result.get('hits', []))}")
            print(f"컨텍스트 길이: {len(result.get('context', ''))}")
        else:
            print(f"응답: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 검색 API 테스트 실패: {e}")
        return False

def test_draft():
    """초안 생성 API 테스트"""
    print("\n🔍 초안 생성 API 테스트...")
    try:
        payload = {
            "question": "2024년 한온시스템 TCFD 보고서 전략 섹션 초안을 작성해줘",
            "sections": ["Strategy"],
            "provider": "openai",
            "style_guide": "ESG/회계 전문용어 기준 유지, 수치/근거 인용",
            "top_k": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/rag/draft",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"생성된 섹션 수: {len(result.get('draft', []))}")
            for section in result.get('draft', []):
                print(f"  - {section['section']}: {len(section['content'])}자")
        else:
            print(f"응답: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 초안 생성 API 테스트 실패: {e}")
        return False

def test_polish():
    """윤문 API 테스트"""
    print("\n🔍 윤문 API 테스트...")
    try:
        payload = {
            "text": "한온시스템은 2024년 TCFD 프레임워크에 따라 기후변화 대응 전략을 수립했습니다. 기업은 탄소중립 목표를 달성하기 위해 다양한 노력을 기울이고 있습니다.",
            "tone": "공식적/객관적",
            "style_guide": "ESG/회계 전문용어 유지, 불필요한 수식어 제거, 한국어 문체 통일",
            "provider": "openai"
        }
        
        response = requests.post(
            f"{BASE_URL}/rag/polish",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"윤문 결과 길이: {len(result.get('polished', ''))}")
            print(f"윤문 결과 미리보기: {result.get('polished', '')[:100]}...")
        else:
            print(f"응답: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 윤문 API 테스트 실패: {e}")
        return False

def test_draft_and_polish():
    """원샷 API 테스트"""
    print("\n🔍 원샷 API 테스트...")
    try:
        payload = {
            "question": "2024년 한온시스템 TCFD 보고서 전략 섹션 초안을 작성해줘",
            "sections": ["Strategy"],
            "provider": "openai",
            "style_guide": "ESG/회계 전문용어 기준 유지, 수치/근거 인용",
            "top_k": 5,
            "tone": "공식적/객관적",
            "polish_style_guide": "ESG/회계 전문용어 유지, 불필요한 수식어 제거, 한국어 문체 통일"
        }
        
        response = requests.post(
            f"{BASE_URL}/rag/draft-and-polish",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"상태 코드: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"생성된 섹션 수: {len(result.get('draft', []))}")
            print(f"윤문 결과 길이: {len(result.get('polished', ''))}")
        else:
            print(f"응답: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 원샷 API 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 LLM Service API 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("헬스체크", test_health),
        ("루트 엔드포인트", test_root),
        ("검색 API", test_search),
        ("초안 생성 API", test_draft),
        ("윤문 API", test_polish),
        ("원샷 API", test_draft_and_polish),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            time.sleep(1)  # API 호출 간격
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n총 {len(results)}개 테스트 중 {passed}개 통과")
    
    if passed == len(results):
        print("🎉 모든 테스트 통과!")
    else:
        print("⚠️ 일부 테스트 실패")

if __name__ == "__main__":
    main()
