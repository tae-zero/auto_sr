# =============================================================================
# 🐳 LLM Service Dockerfile
# =============================================================================
# Docker Compose 및 Railway 배포를 위한 최적화된 Dockerfile
# 2개 RAG 시스템 (OpenAI + Hugging Face) 지원

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
COPY . .

# 스크립트 실행 권한 부여
RUN chmod +x railway-start.sh

# vectordb 디렉토리 생성 (Docker Volume 마운트용)
RUN mkdir -p /app/vectordb/sr_corpus /app/vectordb/standards

# 포트 설정 (Docker Compose에서 8002:8000으로 매핑)
EXPOSE 8000

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행 (Docker Compose 및 Railway 모두 지원)
CMD ["./railway-start.sh"]
