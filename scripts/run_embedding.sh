#!/bin/bash

# RAG 임베딩 실행 스크립트

echo "🚀 RAG 임베딩 프로세스 시작"
echo "=================================="

# 현재 디렉토리를 프로젝트 루트로 변경
cd "$(dirname "$0")/.."

# 가상환경 확인 (선택사항)
if [ -d "venv" ]; then
    echo "📦 가상환경 활성화 중..."
    source venv/bin/activate
fi

# 필요한 패키지 설치
echo "📦 임베딩 패키지 설치 중..."
pip install -r scripts/requirements.embedding.txt

# 임베딩 실행
echo "🔍 임베딩 프로세스 실행 중..."
python scripts/embedding_service.py

echo "✅ 임베딩 프로세스 완료!"
echo "📁 생성된 파일:"
ls -la chroma_db/

echo "=================================="
echo "🎉 RAG 임베딩 시스템 구축 완료!"
