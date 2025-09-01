# =============================================================================
# 🐳 LLM Service Dockerfile (Railway 배포용)
# =============================================================================
# Railway 배포를 위한 최적화된 Dockerfile
# 2개 RAG 시스템 (OpenAI + Hugging Face) 지원
# vectordb는 Railway Volume으로 마운트됨

# Python 3.11 베이스 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
