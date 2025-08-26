# LLM Service

FastAPI + RAG + OpenAI & KoAlpaca(HF/vLLM) API 연동 서비스

## 🚀 개요

이 서비스는 지속가능경영보고서(SR) 13개와 TCFD 기준서 1개를 RAG 파이프라인으로 검색하여 컨텍스트를 구성하고, 생성 모델을 통해 초안과 윤문을 생성하는 백엔드 서비스입니다.

## ✨ 주요 기능

- **RAG 파이프라인**: FAISS 벡터 검색으로 관련 컨텍스트 구성
- **다중 모델 지원**: OpenAI, KoAlpaca(vLLM/TGI), Hugging Face API
- **섹션별 초안 생성**: ESG 보고서 섹션별 전문적인 초안 텍스트 생성
- **자동 윤문**: 문체/용어 일관화 및 중복 제거
- **Railway Volume**: FAISS 인덱스와 문서 스토어의 영구 저장
- **보안**: 관리자 토큰 기반 파일 업로드 보호

## 🏗️ 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   RAG Service   │    │   LLM Service   │
│                 │    │                 │    │                 │
│ • /health       │◄──►│ • FAISS Index  │◄──►│ • OpenAI API   │
│ • /rag/search   │    │ • Doc Store    │    │ • KoAlpaca API │
│ • /rag/draft    │    │ • Embeddings   │    │ • HF API       │
│ • /rag/polish   │    │ • Vector Search│    │                 │
│ • /faiss/upload │    └─────────────────┘    └─────────────────┘
└─────────────────┘              │
                                 │
                    ┌─────────────────┐
                    │ Railway Volume  │
                    │    /data        │
                    │                 │
                    │ • my_index.faiss│
                    │ • doc_store.pkl │
                    └─────────────────┘
```

## 🛠️ 기술 스택

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Vector DB**: FAISS (faiss-cpu)
- **Embeddings**: OpenAI text-embedding-3-small (1536차원)
- **LLM**: OpenAI GPT-4o-mini, KoAlpaca 3.8B, Hugging Face
- **Deployment**: Railway (Docker)
- **Storage**: Railway Volume (/data)

## 📁 디렉토리 구조

```
llm-service/
├── app/
│   ├── main.py              # FastAPI 엔트리포인트
│   ├── rag.py               # RAG 로직 (임베딩, 검색, 프롬프트)
│   ├── llm.py               # LLM API 호출 래퍼
│   ├── schemas.py           # Pydantic 모델
│   ├── security.py          # 토큰 인증
│   ├── utils.py             # 공통 유틸리티
│   └── config.py            # 환경변수 설정
├── data/                    # Railway Volume 마운트 포인트
├── requirements.txt          # Python 의존성
├── Dockerfile               # Docker 이미지
├── env.example              # 환경변수 예시
└── README.md                # 이 파일
```

## 🔧 환경변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```bash
# 서비스 설정
SERVICE_NAME=llm-service
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8002

# FAISS Volume 설정 (Railway Volume)
FAISS_VOLUME_PATH=/data
FAISS_INDEX_NAME=my_index.faiss
FAISS_STORE_NAME=doc_store.pkl

# 임베딩 모델 설정
EMBED_MODEL=text-embedding-3-small
EMBED_DIM=1536
OPENAI_API_KEY=your-openai-api-key

# 생성 모델 설정
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.3

# KoAlpaca API (외부 GPU vLLM/TGI)
GENAI_URL=https://<gpu-host>/v1/chat/completions
GENAI_KEY=<optional>

# Hugging Face API
HF_API_TOKEN=hf_...
HF_MODEL=EleutherAI/polyglot-ko-3.8b

# 보안 설정
ADMIN_TOKEN=supersecret

# 모니터링 설정
LOG_LEVEL=INFO
ENABLE_METRICS=true
ENABLE_LOGGING=true
```

## 🚂 Railway 배포

### 1. Railway 프로젝트 생성

1. [Railway](https://railway.app/)에 로그인
2. "New Project" → "Deploy from GitHub repo" 선택
3. 이 저장소 연결

### 2. Volume 생성 및 마운트

1. Railway 프로젝트에서 "Volumes" 탭 클릭
2. "New Volume" 생성
3. Volume 이름: `llm-data`
4. 마운트 경로: `/data`

### 3. 환경변수 설정

Railway 프로젝트의 "Variables" 탭에서 위의 환경변수들을 설정하세요.

### 4. 배포

GitHub에 푸시하면 자동으로 배포됩니다.

## 📡 API 엔드포인트

### 헬스체크

```bash
GET /health
```

**응답:**
```json
{
  "ok": true,
  "index_loaded": true,
  "store_loaded": true,
  "embed_dim": 1536
}
```

### RAG 검색

```bash
POST /rag/search
```

**요청:**
```json
{
  "question": "한온시스템 TCFD 전략 핵심을 요약해줘",
  "top_k": 8
}
```

**응답:**
```json
{
  "hits": [
    {
      "rank": 1,
      "id": "123",
      "score": 0.95,
      "text": "문서 내용...",
      "meta": {"source": "한온시스템_2024_SR.pdf", "year": "2024"}
    }
  ],
  "context": "[1] 문서 내용... (출처: 한온시스템_2024_SR.pdf)\n\n---\n\n[2] 문서 내용..."
}
```

### 섹션별 초안 생성

```bash
POST /rag/draft
```

**요청:**
```json
{
  "question": "2024년 한온시스템 TCFD 보고서 전략 섹션 초안을 작성해줘",
  "sections": ["Governance", "Strategy", "Risk Management", "Metrics & Targets"],
  "provider": "openai",
  "style_guide": "ESG/회계 전문용어 기준 유지, 수치/근거 인용",
  "top_k": 8
}
```

**응답:**
```json
{
  "draft": [
    {
      "section": "Governance",
      "content": "초안 내용..."
    }
  ],
  "hits": [...]
}
```

### 텍스트 윤문

```bash
POST /rag/polish
```

**요청:**
```json
{
  "text": "초안 텍스트 전체",
  "tone": "공식적/객관적",
  "style_guide": "ESG/회계 전문용어 유지, 불필요한 수식어 제거",
  "provider": "koalpaca"
}
```

**응답:**
```json
{
  "polished": "정제된 텍스트"
}
```

### 초안+윤문 원샷

```bash
POST /rag/draft-and-polish
```

위의 draft와 polish를 순차적으로 실행합니다.

### FAISS 파일 업로드 (관리자 전용)

```bash
POST /faiss/upload
```

**헤더:**
```
X-ADMIN-TOKEN: supersecret
```

**폼 데이터:**
- `index`: FAISS 인덱스 파일 (.faiss)
- `store`: 문서 스토어 파일 (.pkl)

## 🧪 테스트

### 로컬 테스트

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp env.example .env
# .env 파일 편집

# 서비스 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### API 테스트

```bash
# 헬스체크
curl -s http://localhost:8002/health

# 검색
curl -X POST http://localhost:8002/rag/search \
  -H "Content-Type: application/json" \
  -d '{"question":"한온시스템 TCFD 전략","top_k":5}'

# 초안 생성
curl -X POST http://localhost:8002/rag/draft \
  -H "Content-Type: application/json" \
  -d '{
    "question":"2024년 SR 전략 섹션 초안",
    "sections":["Strategy"],
    "provider":"openai",
    "style_guide":"ESG/회계 용어 기준",
    "top_k":8
  }'

# 윤문
curl -X POST http://localhost:8002/rag/polish \
  -H "Content-Type: application/json" \
  -d '{
    "text":"여기에 초안 텍스트",
    "tone":"공식적",
    "style_guide":"ESG/회계 용어 기준",
    "provider":"koalpaca"
  }'

# FAISS 업로드 (관리자)
curl -X POST http://localhost:8002/faiss/upload \
  -H "X-ADMIN-TOKEN: supersecret" \
  -F "index=@my_index.faiss" \
  -F "store=@doc_store.pkl"
```

## 🔒 보안

- `/faiss/upload` 엔드포인트는 `X-ADMIN-TOKEN` 헤더로 보호
- 환경변수 `ADMIN_TOKEN`으로 토큰 설정
- 파일 업로드 시 크기 제한 및 검증

## 📊 모니터링

- 모든 요청에 고유 ID 부여
- 실행 시간 측정 및 로깅
- 에러 발생 시 상세 로그 기록
- 헬스체크로 서비스 상태 모니터링

## 🚨 문제 해결

### 일반적인 문제

1. **FAISS 인덱스 로딩 실패**
   - Volume 마운트 확인
   - 파일 경로 및 권한 확인
   - 임베딩 차원 일치 여부 확인

2. **API 키 오류**
   - 환경변수 설정 확인
   - API 키 유효성 검증

3. **메모리 부족**
   - FAISS 인덱스 크기 확인
   - Railway 리소스 할당 증가

### 로그 확인

```bash
# Railway 로그 확인
railway logs

# 로컬 로그 확인
tail -f app.log
```

## 🤝 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.