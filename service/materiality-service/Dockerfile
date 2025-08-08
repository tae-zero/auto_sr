# Python 3.11 베이스 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# Railway 배포용 포트 설정 (service/materiality-service)
EXPOSE 8003

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_HOST=0.0.0.0
ENV PORT=8003

# Railway의 PORT 환경변수를 사용하여 애플리케이션 실행
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8003}"]
