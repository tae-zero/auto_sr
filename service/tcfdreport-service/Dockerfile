# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치 (배포용)
COPY requirements.prod.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --timeout 600 --retries 3 --verbose -r requirements.prod.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8004

# 환경변수 설정
ENV PYTHONPATH=/app
ENV SERVICE_PORT=8004
ENV PYTHONUNBUFFERED=1

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8004/health || exit 1

# 애플리케이션 실행
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
