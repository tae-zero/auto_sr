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

# 현재 작업 디렉토리 확인
echo "📁 현재 작업 디렉토리: $(pwd)"
echo "📁 현재 디렉토리 내용:"
ls -la

# vectordb 폴더 상태 확인 (Dockerfile에서 복사됨)
echo "🔍 vectordb 폴더 상태 확인:"
if [ -d "/data" ]; then
    echo "  ✅ /data 디렉토리: 존재함"
    echo "  📁 /data 내용:"
    ls -la /data/
    
    if [ -d "/data/sr_corpus" ]; then
        echo "  ✅ sr_corpus 디렉토리: 존재함"
        echo "  📁 sr_corpus 내용:"
        ls -la /data/sr_corpus/
    else
        echo "  ❌ sr_corpus 디렉토리: 존재하지 않음"
    fi
    
    if [ -d "/data/standards" ]; then
        echo "  ✅ standards 디렉토리: 존재함"
        echo "  📁 standards 내용:"
        ls -la /data/standards/
    else
        echo "  ❌ standards 디렉토리: 존재하지 않음"
    fi
else
    echo "  ❌ /data 디렉토리: 존재하지 않음"
    
    # 로컬 vectordb 폴더 확인 (개발 환경용)
    if [ -d "./vectordb" ]; then
        echo "  📁 로컬 vectordb 폴더 발견:"
        ls -la ./vectordb/
        
        # 로컬 vectordb를 /data로 복사
        echo "  📋 로컬 vectordb를 /data로 복사 중..."
        cp -r ./vectordb /data
        echo "  ✅ 복사 완료"
    fi
fi

# Python 의존성 확인
echo "🐍 Python 의존성 확인 중..."
pip list

# 서비스 시작
echo "🌐 서비스 시작..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
