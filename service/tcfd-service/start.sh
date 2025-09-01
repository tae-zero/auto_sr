#!/bin/bash

# Railway 시작 스크립트
echo "🚀 TCFD Service 시작 중..."

# 환경변수 확인
echo "📍 PORT: ${PORT:-8005}"
echo "📍 PYTHONPATH: ${PYTHONPATH:-/app}"

# Python 경로 확인
which python
python --version

# uvicorn 시작
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8005}
