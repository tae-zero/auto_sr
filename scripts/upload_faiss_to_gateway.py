#!/usr/bin/env python3
"""
FAISS 파일을 게이트웨이를 통해 LLM 서비스로 업로드하는 스크립트

사용법:
    python upload_faiss_to_gateway.py --gateway-url <게이트웨이_URL> --index <인덱스_파일> --store <스토어_파일> --token <JWT_토큰>

예시:
    python upload_faiss_to_gateway.py \
        --gateway-url "https://your-gateway.railway.app" \
        --index "my_index.faiss" \
        --store "doc_store.pkl" \
        --token "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
"""

import argparse
import requests
import os
import sys
from pathlib import Path
import json
from typing import Optional

def upload_faiss_files(
    gateway_url: str,
    index_file: str,
    store_file: str,
    jwt_token: str,
    timeout: int = 300
) -> bool:
    """
    FAISS 파일을 게이트웨이를 통해 업로드합니다.
    
    Args:
        gateway_url: 게이트웨이 서비스 URL
        index_file: FAISS 인덱스 파일 경로
        store_file: 문서 스토어 파일 경로
        jwt_token: JWT 인증 토큰
        timeout: 업로드 타임아웃 (초)
    
    Returns:
        bool: 업로드 성공 여부
    """
    try:
        # 파일 존재 확인
        if not os.path.exists(index_file):
            print(f"❌ 인덱스 파일을 찾을 수 없습니다: {index_file}")
            return False
        
        if not os.path.exists(store_file):
            print(f"❌ 스토어 파일을 찾을 수 없습니다: {store_file}")
            return False
        
        # 파일 크기 확인
        index_size = os.path.getsize(index_file)
        store_size = os.path.getsize(index_file)
        
        print(f"📁 파일 정보:")
        print(f"  - 인덱스: {index_file} ({index_size:,} bytes)")
        print(f"  - 스토어: {store_file} ({store_size:,} bytes)")
        
        # 게이트웨이 URL 정리
        if gateway_url.endswith('/'):
            gateway_url = gateway_url[:-1]
        
        upload_url = f"{gateway_url}/faiss/upload"
        
        print(f"🚀 게이트웨이로 업로드 시작: {upload_url}")
        
        # 파일 업로드
        with open(index_file, 'rb') as index_f, open(store_file, 'rb') as store_f:
            files = {
                'index': (os.path.basename(index_file), index_f, 'application/octet-stream'),
                'store': (os.path.basename(store_file), store_f, 'application/octet-stream')
            }
            
            headers = {
                'Authorization': f'Bearer {jwt_token}'
            }
            
            response = requests.post(
                upload_url,
                files=files,
                headers=headers,
                timeout=timeout
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ FAISS 파일 업로드 성공!")
            print(f"📊 응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 업로드 실패: {response.status_code}")
            print(f"📝 응답: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 업로드 타임아웃 ({timeout}초)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 네트워크 오류: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

def check_faiss_status(gateway_url: str, jwt_token: str) -> bool:
    """
    FAISS 상태를 확인합니다.
    
    Args:
        gateway_url: 게이트웨이 서비스 URL
        jwt_token: JWT 인증 토큰
    
    Returns:
        bool: 상태 확인 성공 여부
    """
    try:
        if gateway_url.endswith('/'):
            gateway_url = gateway_url[:-1]
        
        status_url = f"{gateway_url}/faiss/status"
        
        headers = {
            'Authorization': f'Bearer {jwt_token}'
        }
        
        response = requests.get(status_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("🔍 FAISS 상태 확인:")
            print(f"📊 상태: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 상태 확인 실패: {response.status_code}")
            print(f"📝 응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 상태 확인 오류: {e}")
        return False

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="FAISS 파일을 게이트웨이를 통해 LLM 서비스로 업로드",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 로컬 게이트웨이로 업로드
  python upload_faiss_to_gateway.py \\
      --gateway-url "http://localhost:8080" \\
      --index "my_index.faiss" \\
      --store "doc_store.pkl" \\
      --token "your-jwt-token"

  # Railway 게이트웨이로 업로드
  python upload_faiss_to_gateway.py \\
      --gateway-url "https://your-gateway.railway.app" \\
      --index "my_index.faiss" \\
      --store "doc_store.pkl" \\
      --token "your-jwt-token"

  # 상태만 확인
  python upload_faiss_to_gateway.py \\
      --gateway-url "https://your-gateway.railway.app" \\
      --token "your-jwt-token" \\
      --status-only
        """
    )
    
    parser.add_argument(
        '--gateway-url',
        required=True,
        help='게이트웨이 서비스 URL (예: http://localhost:8080 또는 https://your-gateway.railway.app)'
    )
    
    parser.add_argument(
        '--index',
        help='FAISS 인덱스 파일 경로 (예: my_index.faiss)'
    )
    
    parser.add_argument(
        '--store',
        help='문서 스토어 파일 경로 (예: doc_store.pkl)'
    )
    
    parser.add_argument(
        '--token',
        required=True,
        help='JWT 인증 토큰'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='업로드 타임아웃 (초, 기본값: 300)'
    )
    
    parser.add_argument(
        '--status-only',
        action='store_true',
        help='상태만 확인하고 업로드하지 않음'
    )
    
    args = parser.parse_args()
    
    # 상태만 확인하는 경우
    if args.status_only:
        print("🔍 FAISS 상태 확인 모드")
        success = check_faiss_status(args.gateway_url, args.token)
        sys.exit(0 if success else 1)
    
    # 업로드 모드
    if not args.index or not args.store:
        print("❌ --index와 --store 옵션이 필요합니다")
        parser.print_help()
        sys.exit(1)
    
    print("🚀 FAISS 파일 업로드 시작")
    print(f"🌐 게이트웨이: {args.gateway_url}")
    print(f"⏱️  타임아웃: {args.timeout}초")
    
    # 업로드 실행
    success = upload_faiss_files(
        args.gateway_url,
        args.index,
        args.store,
        args.token,
        args.timeout
    )
    
    if success:
        print("\n🎉 업로드 완료! RAG 시스템이 준비되었습니다.")
        
        # 상태 확인
        print("\n🔍 업로드 후 상태 확인...")
        check_faiss_status(args.gateway_url, args.token)
    else:
        print("\n❌ 업로드 실패. 로그를 확인하고 다시 시도해주세요.")
        sys.exit(1)

if __name__ == "__main__":
    main()
