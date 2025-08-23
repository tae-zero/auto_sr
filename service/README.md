# MSA 서비스 디렉토리

이 디렉토리는 ESG Mate 프로젝트의 마이크로서비스들을 포함합니다.

## 🏗️ 아키텍처

모든 서비스는 **MSV Pattern with Layered Architecture**를 따릅니다:

- **Model Layer**: Pydantic 모델 및 데이터 검증
- **Schema Layer**: API 스키마 정의
- **View Layer**: API 엔드포인트 및 컨트롤러
- **Service Layer**: 비즈니스 로직
- **Repository Layer**: 데이터 접근
- **Entity Layer**: 데이터베이스 엔티티

## 🚀 서비스 목록

### 1. **Gateway Service** (`gateway/`)
- **포트**: 8080
- **역할**: API Gateway, 라우팅, 인증, 로드 밸런싱
- **특징**: 모든 서비스의 진입점, JWT 토큰 검증

### 2. **Auth Service** (`auth-service/`)
- **포트**: 8008
- **역할**: 사용자 인증 및 권한 관리
- **특징**: JWT 토큰 발급, 사용자 등록/로그인

### 3. **TCFD Service** (`tcfd-service/`)
- **포트**: 8005
- **역할**: TCFD 프레임워크 기반 기후 리스크 분석
- **특징**: 재무정보 처리, 기후 리스크 평가

### 4. **TCFD Report Service** (`tcfdreport-service/`)
- **포트**: 8004
- **역할**: AI 기반 TCFD 보고서 생성
- **특징**: LangChain 기반, RAG 서비스 통합

### 5. **GRI Service** (`gri-service/`)
- **포트**: 8006
- **역할**: GRI 기준 지속가능성 보고서 생성
- **특징**: GRI 표준 준수, 데이터 분석

### 6. **Materiality Service** (`materiality-service/`)
- **포트**: 8007
- **역할**: Materiality 분석 및 평가
- **특징**: 중요도 매트릭스, 우선순위 분석

### 7. **Chatbot Service** (`chatbot-service/`)
- **포트**: 8001
- **역할**: AI 챗봇 서비스
- **특징**: 사용자 질의 응답, 인증 필요

### 8. **RAG Service** (`rag-service/`)
- **포트**: 8002
- **역할**: Retrieval-Augmented Generation
- **특징**: FAISS + LangChain 기반, 문서 검색 및 생성

## 🔧 공통 설정

### 환경변수
모든 서비스는 다음 환경변수를 공통으로 사용합니다:

```bash
# 서비스 기본 설정
SERVICE_NAME=서비스명
SERVICE_HOST=0.0.0.0
SERVICE_PORT=포트번호
LOG_LEVEL=INFO

# 데이터베이스
DATABASE_URL=postgresql://...

# JWT 설정
JWT_SECRET_KEY=your-secret-key

# 배포 환경
RAILWAY_ENVIRONMENT=false
DEPLOYMENT_ENV=development
```

### 공통 기능
- **로깅**: 구조화된 로깅 시스템
- **예외 처리**: 표준화된 에러 핸들링
- **헬스체크**: `/health` 엔드포인트
- **CORS**: 개발/프로덕션 환경별 설정
- **성능 모니터링**: 함수 실행 시간 추적

## 🐳 Docker 설정

### Dockerfile 공통 사항
- Python 3.11 slim 이미지 사용
- 헬스체크 포함
- 환경변수 기반 설정
- 최적화된 레이어 구조

### 헬스체크
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:포트/health || exit 1
```

## 📊 모니터링

### 헬스체크 스크립트
각 서비스는 독립적인 헬스체크 스크립트를 포함합니다:
- `health_check.py`: Python 기반 헬스체크
- 재시도 로직 포함
- 상세한 오류 정보 제공

### 로깅
- 구조화된 로그 형식
- 서비스별 로그 분리
- 성능 메트릭 포함

## 🚨 오류 처리

### 예외 처리 전략
1. **Graceful Degradation**: DB 연결 실패 시에도 서비스 시작
2. **Retry Logic**: 일시적 오류에 대한 재시도
3. **Circuit Breaker**: 연속 실패 시 서비스 보호
4. **Fallback**: 대체 로직 제공

### 오류 메시지
표준화된 오류 메시지 체계:
- `DATABASE_CONNECTION_FAILED`
- `SERVICE_UNAVAILABLE`
- `INVALID_REQUEST`
- `UNAUTHORIZED`
- `FORBIDDEN`
- `NOT_FOUND`
- `INTERNAL_ERROR`

## 🔄 배포

### 로컬 개발
```bash
# 개별 서비스 실행
cd service/서비스명
python -m uvicorn app.main:app --host 0.0.0.0 --port 포트번호

# Docker Compose로 전체 실행
docker-compose up --build
```

### Railway 배포
- 환경변수 자동 설정
- 포트 자동 할당
- 헬스체크 기반 배포

### Vercel 배포
- 프론트엔드 전용
- 환경변수 설정 필요

## 📝 개발 가이드

### 새 서비스 추가
1. `service/` 디렉토리에 새 폴더 생성
2. `common_config.py` 임포트
3. 표준 main.py 구조 사용
4. 헬스체크 엔드포인트 구현
5. Dockerfile 및 requirements.txt 생성

### 코드 품질
- Type hints 사용
- Docstring 작성
- 예외 처리 구현
- 로깅 추가
- 테스트 코드 작성

## 🔍 문제 해결

### 일반적인 문제
1. **포트 충돌**: `SERVICE_PORT` 환경변수 확인
2. **DB 연결 실패**: `DATABASE_URL` 및 네트워크 설정 확인
3. **의존성 오류**: `requirements.txt` 업데이트
4. **권한 문제**: Docker 권한 및 파일 권한 확인

### 디버깅
- 로그 레벨을 `DEBUG`로 설정
- 헬스체크 엔드포인트 확인
- Docker 로그 분석
- 네트워크 연결 테스트

## 📚 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [MSV Pattern 가이드](https://github.com/your-repo/msv-pattern)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Microservices Patterns](https://microservices.io/patterns/)
