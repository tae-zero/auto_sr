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

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 의존성 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY app/ ./app/
COPY railway-start.sh .
COPY railway.json .
COPY Procfile .
COPY runtime.txt .

# vectordb 폴더 복사 (Railway 볼륨에 복사할 소스)
COPY ../tcfdreport-service/vectordb/ ./vectordb/

# 스크립트 실행 권한 부여
RUN chmod +x railway-start.sh

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 애플리케이션 실행
CMD ["./railway-start.sh"]
