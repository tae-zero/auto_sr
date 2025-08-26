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

# vectordb 폴더 상태 확인 (Railway Volume 경로 사용)
echo "🔍 vectordb 폴더 상태 확인:"
if [ -d "$FAISS_VOLUME_PATH" ]; then
    echo "  ✅ $FAISS_VOLUME_PATH 디렉토리: 존재함"
    echo "  📁 $FAISS_VOLUME_PATH 내용:"
    ls -la "$FAISS_VOLUME_PATH"
    
    if [ -d "$FAISS_VOLUME_PATH/$FAISS_INDEX_NAME" ]; then
        echo "  ✅ $FAISS_INDEX_NAME 디렉토리: 존재함"
        echo "  📁 $FAISS_INDEX_NAME 내용:"
        ls -la "$FAISS_VOLUME_PATH/$FAISS_INDEX_NAME"
    else
        echo "  ❌ $FAISS_INDEX_NAME 디렉토리: 존재하지 않음"
    fi
    
    if [ -d "$FAISS_VOLUME_PATH/standards" ]; then
        echo "  ✅ standards 디렉토리: 존재함"
        echo "  📁 standards 내용:"
        ls -la "$FAISS_VOLUME_PATH/standards"
    else
        echo "  ❌ standards 디렉토리: 존재하지 않음"
    fi
else
    echo "  ❌ $FAISS_VOLUME_PATH 디렉토리: 존재하지 않음"
    echo "  📁 Railway Volume에 vectordb 폴더를 업로드해야 합니다"
    echo "  📁 예상 경로: $FAISS_VOLUME_PATH/$FAISS_INDEX_NAME/index.faiss"
fi

# Python 의존성 확인
echo "🐍 Python 의존성 확인 중..."
pip list

# 서비스 시작
echo "🌐 서비스 시작..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
