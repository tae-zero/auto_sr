# Python 3.11 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치 (안정적인 방식)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# fonts 폴더 복사 (한글 폰트 지원)
COPY fonts/ ./fonts/

# 애플리케이션 코드 복사
COPY . .

# 시작 스크립트에 실행 권한 부여 (윈도우에서 권한 비트가 사라지는 문제 대비)
RUN chmod +x /app/start.sh || true

# 포트 노출
EXPOSE 8005

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Railway 시작 명령어 (직접 Python 실행으로 권한 문제 완전 해결)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005"]