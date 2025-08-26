# 🤖 LLM Service

2개 RAG 시스템을 지원하는 지속가능경영보고서 분석 서비스 (OpenAI + Hugging Face)

## 🚀 주요 기능

- **OpenAI RAG**: GPT-4o-mini를 사용한 텍스트 생성
- **Hugging Face RAG**: KoAlpaca/RoLA 모델을 사용한 텍스트 생성
- **FAISS 벡터 검색**: 이미 임베딩된 FAISS 인덱스 사용
- **TCFD 보고서 생성**: 기후 관련 재무정보 공시 보고서 자동 생성

## 🏗️ 아키텍처

- **MSA + MVC**: Microservice Architecture + Model-View-Controller
- **FastAPI**: 고성능 Python 웹 프레임워크
- **FAISS**: Facebook AI Similarity Search (벡터 데이터베이스)

## 📁 프로젝트 구조

```
app/
├── common/           # 공통 설정 및 유틸리티
├── domain/           # 도메인 로직
│   ├── rag/         # RAG 서비스 구현
│   └── llm/         # LLM 서비스 구현
├── router/           # API 라우터
└── www/             # 웹 관련 미들웨어
```

## 🐳 Docker 배포

### Docker Compose로 로컬 실행
```bash
# 전체 서비스 실행
docker-compose up -d

# llm-service만 실행
docker-compose up -d llm-service

# 로그 확인
docker-compose logs -f llm-service
```

### 단독 Docker 실행
```bash
docker build -t llm-service .
docker run -p 8002:8000 llm-service
```

### Railway 배포
```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인 및 배포
railway login
railway link
railway up
```

## 🔧 환경변수

### 필수 환경변수
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Hugging Face API
HF_API_TOKEN=your_hf_token

# FAISS 설정
FAISS_VOLUME_PATH=./vectordb
EMBED_DIM=1536

# 보안
ADMIN_TOKEN=your_admin_token
```

### Railway 환경변수
```bash
# Railway에서 자동 설정
PORT=8000
RAILWAY_ENVIRONMENT=production
```

## 📚 API 엔드포인트

- `GET /`: 서비스 정보
- `GET /health`: 헬스체크
- `POST /rag/search`: 문서 검색
- `POST /rag/draft`: 초안 생성
- `POST /rag/polish`: 텍스트 윤문
- `POST /rag/draft-and-polish`: 초안+윤문 원샷
- `POST /rag/faiss/upload`: FAISS 파일 업로드
- `GET /rag/faiss/status`: FAISS 상태 확인

## 🚀 시작하기

1. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   ```

2. **환경변수 설정**
   ```bash
   cp env.example .env
   # .env 파일 편집
   ```

3. **서비스 실행**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **API 문서 확인**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## 🔍 문제 해결

### Railway 배포 오류
- `Dockerfile`이 존재하는지 확인
- `requirements.txt`의 의존성 버전 호환성 확인
- 환경변수 설정 확인

### FAISS 인덱스 로딩 오류
- `vectordb/` 디렉토리 구조 확인
- 파일 권한 확인
- 메모리 사용량 확인

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 로그 확인: `railway logs`
2. 환경변수 확인: `railway variables`
3. 헬스체크: `/health` 엔드포인트