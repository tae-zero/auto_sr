# 🐳 LLM Service Docker Compose 환경변수 설정 가이드

## 📋 루트 .env 파일에 추가할 환경변수

```bash
# =============================================================================
# LLM Service 설정
# =============================================================================

# 포트 설정
LLM_SERVICE_PORT=8002

# FAISS 설정
EMBED_DIM=1536

# OpenAI 설정
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.3

# Hugging Face 설정
HF_API_TOKEN=your_huggingface_token_here
HF_MODEL=EleutherAI/polyglot-ko-3.8b

# 외부 GPU 설정 (선택사항)
GENAI_URL=your_genai_url_here
GENAI_KEY=your_genai_key_here

# 보안 설정
ADMIN_TOKEN=supersecret

# 모니터링 설정
ENABLE_METRICS=true
ENABLE_LOGGING=true

# 유틸리티 설정
MAX_FILE_SIZE=20971520
SUPPORTED_FILE_TYPES=txt,pdf,docx,md
DEFAULT_TOP_K=5
MAX_TOP_K=20
```

## 🚀 Docker Compose 실행 명령어

```bash
# 전체 서비스 실행
docker-compose up -d

# llm-service만 실행
docker-compose up -d llm-service

# 로그 확인
docker-compose logs -f llm-service

# 서비스 상태 확인
docker-compose ps

# 서비스 중지
docker-compose down
```

## 🔍 서비스 접속 확인

- **LLM Service**: http://localhost:8002
- **Health Check**: http://localhost:8002/health
- **API Docs**: http://localhost:8002/docs

## 📁 볼륨 마운트 확인

```bash
# vectordb 데이터 확인
docker exec -it llm-service ls -la /app/vectordb/

# 로그 확인
docker exec -it llm-service cat /app/railway-start.sh
```

## ⚠️ 주의사항

1. **FAISS 파일**: `vectordb/` 폴더의 FAISS 인덱스와 pkl 파일이 Docker 볼륨에 마운트됩니다.
2. **환경변수**: OpenAI API 키와 Hugging Face 토큰은 반드시 설정해야 합니다.
3. **포트 충돌**: 8002 포트가 이미 사용 중인 경우 다른 포트로 변경하세요.
4. **메모리**: RAG 서비스는 충분한 메모리가 필요합니다 (최소 2GB 권장).
