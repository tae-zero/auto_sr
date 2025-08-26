# LLM Service MSA 구조

이 문서는 `llm-service`의 MSA(Microservice Architecture) 구조를 설명합니다.

## 🏗️ 전체 아키텍처

```
llm-service/
├── app/
│   ├── main.py                    # 🚀 FastAPI 엔트리포인트
│   ├── common/                    # 🔧 공통 유틸리티
│   │   ├── __init__.py
│   │   ├── config.py             # 환경변수 및 설정
│   │   ├── schemas.py            # Pydantic 모델
│   │   └── utils.py              # 공통 유틸리티 함수
│   ├── domain/                    # 🎯 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── rag/                  # RAG 도메인
│   │   │   ├── __init__.py
│   │   │   └── rag_service.py    # RAG 서비스 로직
│   │   └── llm/                  # LLM 도메인
│   │       ├── __init__.py
│   │       └── llm_service.py    # LLM 서비스 로직
│   ├── router/                    # 🌐 API 엔드포인트
│   │   ├── __init__.py
│   │   └── rag_router.py         # RAG 관련 라우터
│   └── www/                      # 🌍 웹 관련
│       ├── __init__.py
│       └── security.py           # 보안 및 인증
├── data/                          # 📁 Railway Volume 마운트
├── requirements.txt               # 📦 Python 의존성
├── Dockerfile                     # 🐳 Docker 이미지
├── railway.json                   # 🚂 Railway 설정
└── README.md                      # 📖 프로젝트 문서
```

## 📁 폴더별 역할

### 1. `app/common/` - 공통 유틸리티
- **config.py**: 환경변수, 설정값, 상수 정의
- **schemas.py**: Pydantic 모델 (요청/응답 스키마)
- **utils.py**: 공통 유틸리티 함수 (로깅, 파일 처리 등)

### 2. `app/domain/` - 비즈니스 로직
- **rag/**: RAG (Retrieval-Augmented Generation) 도메인
  - `rag_service.py`: FAISS 인덱스 관리, 벡터 검색 로직
- **llm/**: LLM (Large Language Model) 도메인
  - `llm_service.py`: OpenAI, KoAlpaca, HF API 호출 로직

### 3. `app/router/` - API 엔드포인트
- **rag_router.py**: RAG 관련 모든 엔드포인트 정의
  - `/rag/search`: 문서 검색
  - `/rag/draft`: 섹션별 초안 생성
  - `/rag/polish`: 텍스트 윤문
  - `/rag/draft-and-polish`: 초안+윤문 원샷
  - `/rag/faiss/upload`: FAISS 파일 업로드

### 4. `app/www/` - 웹 관련
- **security.py**: 관리자 토큰 인증, 보안 미들웨어

### 5. `app/main.py` - 애플리케이션 엔트리포인트
- FastAPI 앱 초기화
- 미들웨어 설정
- 라우터 등록
- 전역 예외 처리

## 🔄 데이터 흐름

```
Client Request
     ↓
main.py (라우팅)
     ↓
router/rag_router.py (엔드포인트 처리)
     ↓
domain/rag/rag_service.py (RAG 로직)
domain/llm/llm_service.py (LLM 로직)
     ↓
common/schemas.py (응답 모델)
     ↓
Client Response
```

## 🎯 MSA 설계 원칙

### 1. **관심사 분리 (Separation of Concerns)**
- 각 폴더는 명확한 책임을 가짐
- 비즈니스 로직과 API 로직 분리

### 2. **의존성 역전 (Dependency Inversion)**
- 상위 모듈이 하위 모듈에 의존하지 않음
- 인터페이스를 통한 느슨한 결합

### 3. **단일 책임 원칙 (Single Responsibility)**
- 각 서비스는 하나의 책임만 가짐
- RAG 서비스: 검색과 컨텍스트 구성
- LLM 서비스: 텍스트 생성과 윤문

### 4. **개방-폐쇄 원칙 (Open-Closed)**
- 새로운 LLM 프로바이더 추가 시 기존 코드 수정 없이 확장 가능
- 새로운 RAG 기능 추가 시 기존 서비스 영향 없음

## 🚀 확장성

### 새로운 LLM 프로바이더 추가
1. `domain/llm/llm_service.py`에 새 메서드 추가
2. `common/schemas.py`의 `ProviderEnum`에 새 값 추가
3. 기존 코드 수정 없이 확장 완료

### 새로운 RAG 기능 추가
1. `domain/rag/rag_service.py`에 새 메서드 추가
2. `router/rag_router.py`에 새 엔드포인트 추가
3. 기존 서비스 영향 없음

### 새로운 도메인 추가
1. `domain/` 하위에 새 폴더 생성
2. `router/` 하위에 새 라우터 생성
3. `main.py`에 새 라우터 등록

## 🔧 개발 가이드

### 로컬 개발
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp env.example .env
# .env 파일 편집

# 서비스 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### 테스트
```bash
# API 테스트
python test_api.py

# 개별 모듈 테스트
python -m pytest app/domain/rag/tests/
python -m pytest app/domain/llm/tests/
```

### 배포
```bash
# Docker 빌드
docker build -t llm-service .

# Docker 실행
docker run -p 8002:8002 llm-service

# Railway 배포
# GitHub 푸시 시 자동 배포
```

## 📊 모니터링 및 로깅

- 모든 요청에 고유 ID 부여
- 실행 시간 측정 및 로깅
- 에러 발생 시 상세 로그 기록
- 헬스체크로 서비스 상태 모니터링

## 🔒 보안

- 관리자 토큰 기반 파일 업로드 보호
- 환경변수를 통한 민감 정보 관리
- 파일 업로드 시 크기 및 타입 검증

이 MSA 구조를 통해 `llm-service`는 확장 가능하고 유지보수가 용이한 아키텍처를 제공합니다.
