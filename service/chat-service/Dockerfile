FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8006

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8006/health || exit 1

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV SERVICE_HOST=0.0.0.0
ENV SERVICE_PORT=8006
ENV LOG_LEVEL=INFO

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8006"] 