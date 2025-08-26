#!/bin/bash

# =============================================================================
# 🚀 LLM Service 시작 스크립트 (Docker Compose + Railway 지원)
# =============================================================================

echo "🚀 LLM Service 시작 중..."

# 환경변수 확인
echo "📋 환경변수 확인:"
echo "  - PORT: $PORT"
echo "  - SERVICE_HOST: $SERVICE_HOST"
echo "  - FAISS_VOLUME_PATH: $FAISS_VOLUME_PATH"
echo "  - FAISS_INDEX_NAME: $FAISS_INDEX_NAME"
echo "  - FAISS_STORE_NAME: $FAISS_STORE_NAME"

# vectordb 디렉토리 생성 (Docker Volume 마운트 지원)
mkdir -p /app/vectordb/sr_corpus
mkdir -p /app/vectordb/standards

echo "📁 vectordb 디렉토리 생성 완료"

# FAISS 파일 상태 확인
echo "🔍 FAISS 파일 상태 확인:"
if [ -f "/app/vectordb/sr_corpus/index.faiss" ]; then
    echo "  ✅ sr_corpus/index.faiss: 존재함"
    ls -la /app/vectordb/sr_corpus/
else
    echo "  ❌ sr_corpus/index.faiss: 존재하지 않음"
fi

if [ -f "/app/vectordb/standards/index.faiss" ]; then
    echo "  ✅ standards/index.faiss: 존재함"
    ls -la /app/vectordb/standards/
else
    echo "  ❌ standards/index.faiss: 존재하지 않음"
fi

# Python 의존성 확인
echo "🐍 Python 의존성 확인 중..."
pip list

# 서비스 시작
echo "🌐 서비스 시작..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
