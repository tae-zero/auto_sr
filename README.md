# ESG Mate - AI 기반 ESG 분석 및 보고서 생성 플랫폼

## 🚀 프로젝트 개요

**ESG Mate**는 기업의 ESG(환경, 사회, 거버넌스) 성과를 AI 기술로 분석하고, TCFD, GRI 등 국제 표준에 맞는 전문 보고서를 자동으로 생성하는 통합 플랫폼입니다.

## 🏗️ 전체 시스템 아키텍처

### Frontend (Next.js 15.4.5)
- **React 19.1.0 + TypeScript 5.9.2**: 최신 프론트엔드 기술 스택
- **Tailwind CSS 3.4.17**: 반응형 및 모던한 UI/UX
- **Zustand 5.0.7**: 효율적인 상태 관리
- **Next.js PWA**: Progressive Web App 지원
- **반응형 디자인**: 모든 디바이스에서 최적화된 사용자 경험

#### 🎨 주요 페이지 및 기능
- **메인 대시보드**: 포트폴리오 스타일의 통합 진입점
- **TCFD SR**: AI 기반 TCFD 보고서 생성 및 다운로드
- **재무대시보드**: 유가증권시장 데이터 시각화
- **ESG 공시 챗봇**: GRI, TCFD, KSSB, IFRS 기준 질의응답
- **Climate**: 기후 데이터 갤러리 및 시각화
- **Climate Scenarios**: SSP2.6, SSP8.5 기후 시나리오 분석
- **Materiality**: 중요도 분석 및 평가 시스템
- **GRI INDEX**: GRI 표준 지표 데이터베이스
- **My Gallery**: 개인 포토 갤러리

#### 🔐 인증 시스템
- **JWT 토큰 기반**: 안전한 사용자 인증
- **자동 토큰 갱신**: 만료 시 자동 갱신 메커니즘
- **회사별 데이터 격리**: 사용자별 접근 권한 관리
- **로그인/회원가입**: 통합 인증 서비스 연동

### Backend (Microservices Architecture)

#### 1. Gateway Service (포트: 8000)
- **API 게이트웨이**: 모든 서비스 요청의 진입점
- **서비스 디스커버리**: 동적 서비스 라우팅 및 상태 모니터링
- **통합 인증**: JWT 토큰 기반 보안 및 권한 검증
- **로드 밸런싱**: 트래픽 분산 및 관리
- **프록시 라우팅**: 각 마이크로서비스로 요청 전달
- **CORS 관리**: 크로스 오리진 요청 처리
- **환경별 설정**: 로컬/프로덕션 환경 자동 감지

#### 2. LLM Service (포트: 8002)
- **OpenAI GPT-4o-mini**: 글로벌 최고 수준의 언어 모델
- **KoAlpaca/RoLA**: 한국어 특화 자연스러운 표현
- **RAG 시스템**: LangChain 기반 문서 검색 및 생성
- **Vector Database**: ChromaDB를 활용한 의미론적 검색
- **FAISS 인덱스**: 고성능 벡터 검색 엔진
- **문서 임베딩**: 다차원 벡터 공간에서 유사도 계산
- **AI 모델 선택**: OpenAI 또는 Hugging Face 모델 선택 가능

##### 🔍 RAG 검색 기능
- **문서 검색**: 질의어 기반 관련 문서 검색
- **초안 생성**: 섹션별 AI 보고서 초안 생성
- **윤문 생성**: 초안을 바탕으로 한 정제된 텍스트 생성
- **통합 생성**: 초안과 윤문을 동시에 생성
- **관련성 점수**: 가중치 기반 문서 관련성 평가
- **임계값 조정**: 검색 정확도 조절 가능

#### 3. TCFD Service (포트: 8003)
- **TCFD 프레임워크**: 4개 핵심 영역 지원
  - 거버넌스 (Governance): 기후변화 대응 조직 구조
  - 전략 (Strategy): 기후변화 위험 및 기회 분석
  - 위험관리 (Risk Management): 기후 위험 식별 및 평가
  - 지표 및 목표 (Metrics & Targets): 성과 측정 및 목표 설정
- **기후 시나리오 분석**: SSP2.6, SSP8.5 시나리오별 예측
- **데이터 표준화**: 국제 표준 준수
- **MSV 아키텍처**: Controller-Service-Repository 패턴
- **재무정보 처리**: 기업 재무 데이터 분석 및 가공

##### 📊 TCFD 데이터 스키마
- **TCFD 표준 정보**: 공개 요구사항 및 가이드라인
- **기후 위험 평가**: 물리적/전환 위험 분석
- **재무 지표**: ESG 성과 측정 지표
- **기후 시나리오**: 다양한 온도 상승 시나리오
- **준수성 검사**: TCFD 표준 준수 여부 확인

#### 4. TCFD Report Service (포트: 8004)
- **AI 보고서 생성**: TCFD 프레임워크 기반 자동 생성
- **문서 다운로드**: Word(.docx) 및 PDF 형식 지원
- **회사별 맞춤**: 개인화된 보고서 생성
- **품질 관리**: 전문적인 문서 포맷팅 및 검증
- **LangChain 통합**: RAG 기반 지식 검색 및 활용
- **ChromaDB 연동**: 벡터 데이터베이스 기반 문서 검색

##### 📄 문서 생성 기능
- **Word 문서**: python-docx 기반 전문 보고서
- **PDF 변환**: WeasyPrint 기반 고품질 PDF 생성
- **한글 폰트 지원**: Noto Sans KR, Malgun Gothic 폰트 적용
- **템플릿 시스템**: 표준화된 보고서 구조
- **오류 처리**: PDF 생성 실패 시 HTML fallback 제공

##### 🔧 기술적 특징
- **WeasyPrint 61.2**: 최신 PDF 생성 엔진
- **한글 폰트 패키지**: fonts-noto-cjk, fonts-nanum
- **시스템 의존성**: libcairo2, libpango, libgdk-pixbuf-xlib-2.0-0
- **Docker 최적화**: Debian 13 (trixie) 호환성

#### 5. Materiality Service (포트: 8005)
- **중요도 분석**: ESG 이슈별 우선순위 평가
- **스테이크홀더 참여**: 이해관계자 의견 수렴
- **데이터 시각화**: 중요도 매트릭스 및 차트
- **다중 표준 지원**: KCGS, SASB, 서스틴베스트 통합
- **업종별 맞춤**: 산업별 특성에 맞는 중요도 평가

##### 📋 중요도 분석 데이터
- **카테고리별 분류**: 환경(E), 사회(S), 거버넌스(G)
- **KCGS 지표**: 한국기업지배구조원 중요도 지표
- **SASB 표준**: Sustainability Accounting Standards Board
- **서스틴베스트**: 지속가능성 평가 전문 기관

#### 6. GRI Service
- **GRI 표준**: 글로벌 지속가능성 보고 표준
- **지표 데이터베이스**: GRI 지표별 가이드라인
- **보고서 템플릿**: GRI 표준 준수 템플릿 제공
- **준수성 검증**: GRI 표준 준수 여부 확인

#### 7. Auth Service (포트: 8008)
- **JWT 인증**: 안전한 사용자 인증 시스템
- **권한 관리**: 역할 기반 접근 제어 (RBAC)
- **회사별 데이터 격리**: 보안 강화
- **MSV 아키텍처**: Layered Architecture 패턴
- **PostgreSQL 연동**: 사용자 데이터 영구 저장

##### 🔐 인증 기능
- **사용자 등록**: 회사 정보, 업종, 개인정보 포함
- **로그인/로그아웃**: JWT 토큰 기반 세션 관리
- **토큰 검증**: API 요청 시 권한 확인
- **토큰 갱신**: 만료 시 자동 갱신
- **비밀번호 관리**: 안전한 비밀번호 저장 및 검증

#### 8. Chatbot Service
- **AI 챗봇**: ESG 관련 질의응답
- **자연어 처리**: 한국어/영어 다국어 지원
- **지식 베이스**: ESG 표준 및 가이드라인 연동
- **대화 히스토리**: 사용자별 대화 기록 관리

## 🎯 주요 기능

### 1. AI 기반 ESG 분석
- **자동 데이터 수집**: 기업 재무 및 ESG 데이터 통합
- **스마트 분석**: AI 알고리즘을 통한 패턴 인식
- **예측 모델링**: 기후 위험 및 기회 시나리오 분석
- **RAG 검색**: 관련 문서 자동 검색 및 활용

### 2. 표준 준수 보고서 생성
- **TCFD 보고서**: 기후 관련 재무정보 공시
- **GRI 보고서**: 지속가능성 성과 보고
- **통합 ESG 보고서**: 다중 표준 통합 분석
- **AI 윤문**: 초안을 바탕으로 한 전문적 텍스트 생성

### 3. 문서 다운로드 시스템
- **Word 문서 (.docx)**: 편집 가능한 전문 보고서
- **PDF 문서**: 인쇄 및 공유 최적화
- **Excel 데이터**: 원본 데이터 및 분석 결과
- **HTML Fallback**: PDF 생성 실패 시 대체 형식

### 4. 대시보드 및 시각화
- **실시간 모니터링**: ESG 지표 실시간 추적
- **인터랙티브 차트**: 데이터 탐색 및 분석
- **비교 분석**: 업계 평균 대비 성과 비교
- **기후 시나리오**: SSP2.6, SSP8.5 시나리오별 시각화

### 5. 기후 데이터 분석
- **ONI 시계열**: Oceanic Niño Index 분석
- **AMO 상관관계**: Atlantic Multidecadal Oscillation
- **DPR Z-프로파일**: Dual-frequency Precipitation Radar
- **온도 이상**: 수직 단면도 및 글로벌 맵
- **강수량 분석**: 강수 강도, 호우일수, 무강수 지속기간

## 📱 사용자 인터페이스

### 대시보드
- **ESG 스코어**: 종합 ESG 성과 지표
- **기후 위험**: 기후변화 영향도 분석
- **재무 연관성**: ESG 성과와 재무 성과의 상관관계
- **포트폴리오 스타일**: 직관적인 네비게이션

### 보고서 생성
- **데이터 입력**: 회사 정보 및 ESG 데이터 입력
- **AI 모델 선택**: OpenAI 또는 KoAlpaca 모델 선택
- **실시간 생성**: AI 기반 보고서 자동 생성
- **품질 검토**: 생성된 보고서 검토 및 수정
- **섹션별 편집**: 거버넌스, 전략, 위험관리, 지표별 개별 편집

### 다운로드 센터
- **형식 선택**: Word, PDF, Excel 중 선택
- **일괄 다운로드**: 여러 보고서 동시 다운로드
- **버전 관리**: 보고서 버전별 이력 관리
- **파일명 자동화**: 회사명_보고서_날짜시간 형식

## 🛠️ 기술 스택

### Frontend
- **Next.js 15.4.5**: React 기반 풀스택 프레임워크
- **TypeScript 5.9.2**: 타입 안전성 보장
- **Tailwind CSS 3.4.17**: 유틸리티 퍼스트 CSS 프레임워크
- **Zustand 5.0.7**: 경량 상태 관리 라이브러리
- **Axios 1.11.0**: HTTP 클라이언트
- **Next PWA 5.6.0**: Progressive Web App 지원

### Backend
- **FastAPI**: 고성능 Python 웹 프레임워크
- **PostgreSQL**: 관계형 데이터베이스
- **Redis**: 캐싱 및 세션 저장소
- **Celery**: 비동기 작업 큐
- **SQLAlchemy**: ORM 및 데이터베이스 추상화
- **asyncpg**: 비동기 PostgreSQL 드라이버

### AI/ML
- **LangChain**: LLM 애플리케이션 프레임워크
- **ChromaDB**: 벡터 데이터베이스
- **OpenAI API**: GPT 모델 통합
- **Hugging Face**: 오픈소스 AI 모델
- **FAISS**: Facebook AI Similarity Search
- **Sentence Transformers**: 텍스트 임베딩 모델

### 문서 처리
- **python-docx 1.1.0**: Word 문서 생성 및 편집
- **WeasyPrint 61.2**: HTML to PDF 변환
- **pydyf**: PDF 생성 핵심 라이브러리
- **tinycss2**: CSS 파싱 및 처리
- **cssselect2**: CSS 선택자 처리

### DevOps
- **Docker**: 컨테이너화
- **Kubernetes**: 컨테이너 오케스트레이션
- **Railway**: 클라우드 배포 플랫폼
- **GitHub Actions**: CI/CD 파이프라인
- **Debian 13 (trixie)**: 컨테이너 운영체제

## 🚀 설치 및 실행

### Prerequisites
- Docker & Docker Compose
- Node.js 20.x
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Quick Start
```bash
# 1. 저장소 클론
git clone <repository-url>
cd auto_sr

# 2. 환경 변수 설정
cp env.example .env
# .env 파일 편집하여 필요한 값 설정

# 3. Docker Compose로 모든 서비스 실행
docker-compose up -d

# 4. 프론트엔드 접속
# http://localhost:3001

# 5. API 문서 확인
# http://localhost:8000/docs
```

## 🔧 환경 변수 설정

### 필수 설정
```bash
# 데이터베이스
DATABASE_URL=postgresql://user:password@localhost:5432/esgmate
REDIS_URL=redis://localhost:6379

# JWT 인증
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# OpenAI API
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Hugging Face
HF_API_TOKEN=your-huggingface-token
HF_MODEL=beomi/KoAlpaca-Polyglot-12.8B

# 서비스 포트
GATEWAY_PORT=8000
LLM_SERVICE_PORT=8002
TCFD_SERVICE_PORT=8003
TCFD_REPORT_SERVICE_PORT=8004
MATERIALITY_SERVICE_PORT=8005
AUTH_SERVICE_PORT=8008
CHATBOT_SERVICE_PORT=8007

# Railway 환경
RAILWAY_ENVIRONMENT=true
RAILWAY_AUTH_SERVICE_URL=https://auth-service-production.up.railway.app
```

## 📚 API 문서

### Gateway Service
- `GET /docs`: 통합 API 문서 (Swagger UI)
- `GET /health`: 서비스 상태 확인
- `GET /api/v1/services`: 등록된 서비스 목록

### TCFD Report Service
- `POST /api/v1/tcfdreport/download/word`: Word 문서 다운로드
- `POST /api/v1/tcfdreport/download/pdf`: PDF 다운로드
- `POST /api/v1/tcfdreport/inputs`: TCFD 입력 데이터 생성
- `GET /api/v1/tcfdreport/inputs/{company_name}`: 회사별 TCFD 데이터 조회

### LLM Service
- `POST /api/v1/llm/generate`: AI 모델을 통한 텍스트 생성
- `POST /api/v1/llm/rag`: RAG 기반 문서 검색 및 생성
- `POST /api/v1/llm/draft`: 섹션별 초안 생성
- `POST /api/v1/llm/polish`: 초안 윤문 생성
- `POST /api/v1/llm/draft-and-polish`: 초안과 윤문 동시 생성

### TCFD Service
- `GET /api/v1/tcfd/standards`: TCFD 표준 정보 조회
- `GET /api/v1/tcfd/standards/{category}`: 카테고리별 TCFD 표준
- `POST /api/v1/tcfd/analysis`: TCFD 분석 수행
- `GET /api/v1/tcfd/climate-scenarios`: 기후 시나리오 데이터

### Auth Service
- `POST /api/v1/auth/login`: 사용자 로그인
- `POST /api/v1/auth/signup`: 사용자 등록
- `GET /api/v1/auth/verify`: 토큰 검증
- `POST /api/v1/auth/refresh`: 토큰 갱신

### Materiality Service
- `GET /api/v1/materiality/data/categories`: 중요도 카테고리 데이터
- `GET /api/v1/materiality/data/kcgs`: KCGS 중요도 지표
- `GET /api/v1/materiality/data/sasb`: SASB 표준 데이터
- `GET /api/v1/materiality/data/sustainbest-{e|s|g}`: 서스틴베스트 지표

## 🔒 보안 및 인증

### 인증 시스템
- **JWT 토큰**: 안전한 사용자 인증
- **토큰 갱신**: 자동 토큰 갱신 메커니즘
- **세션 관리**: 보안 세션 관리
- **권한 검증**: API 요청 시 자동 권한 확인

### 데이터 보안
- **암호화**: 민감 데이터 암호화 저장
- **접근 제어**: 역할 기반 권한 관리
- **감사 로그**: 모든 접근 기록 추적
- **회사별 격리**: 사용자 데이터 완전 분리

## 📊 성능 및 확장성

### 성능 최적화
- **캐싱**: Redis를 통한 응답 속도 향상
- **비동기 처리**: Celery를 통한 백그라운드 작업
- **로드 밸런싱**: 트래픽 분산 처리
- **벡터 검색**: FAISS 기반 고성능 유사도 검색

### 확장성
- **마이크로서비스**: 독립적인 서비스 확장
- **컨테이너화**: Docker 기반 배포
- **클라우드 네이티브**: Railway 등 클라우드 플랫폼 지원
- **수평 확장**: 서비스별 독립적 스케일링

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의 및 지원

- **이슈 리포트**: GitHub Issues를 통한 버그 리포트
- **기능 제안**: 새로운 기능 아이디어 제안
- **기술 지원**: 개발 관련 질문 및 답변

## 🚀 로드맵

### Phase 1 (현재)
- ✅ 기본 MSA 아키텍처 구축
- ✅ TCFD 보고서 생성 시스템
- ✅ Word/PDF 다운로드 기능
- ✅ 기본 AI 모델 통합
- ✅ RAG 검색 시스템
- ✅ 사용자 인증 시스템
- ✅ 기후 데이터 시각화

### Phase 2 (계획)
- 🔄 GRI 보고서 시스템 강화
- 🔄 고급 데이터 시각화
- 🔄 모바일 앱 개발
- 🔄 다국어 지원 확대
- 🔄 실시간 알림 시스템
- 🔄 고급 분석 대시보드

### Phase 3 (미래)
- 📋 블록체인 기반 데이터 검증
- 📋 AI 예측 모델 고도화
- 📋 글로벌 ESG 표준 통합
- 📋 엔터프라이즈급 보안 강화
- 📋 머신러닝 기반 위험 예측
- 📋 자동화된 ESG 감사 시스템

---

**ESG Mate** - 지속가능한 미래를 위한 AI 기반 ESG 분석 플랫폼 🚀

*모든 서비스를 통합하여 제공하는 완전한 ESG 분석 솔루션*

## 📋 프로젝트 상세 분석 요약

### 🎯 **프로젝트 핵심 가치**
이 프로젝트는 **AI 기술을 활용한 ESG 분석의 민주화**를 목표로 합니다. 복잡한 ESG 표준과 데이터를 AI가 자동으로 분석하고, 전문가 수준의 보고서를 생성하여 모든 기업이 쉽게 ESG 공시를 수행할 수 있도록 지원합니다.

### 🔧 **기술적 혁신**
- **RAG 시스템**: LangChain과 ChromaDB를 활용한 지능형 문서 검색
- **멀티 모달 AI**: OpenAI와 KoAlpaca 모델의 하이브리드 활용
- **MSA 아키텍처**: 확장 가능하고 유지보수가 용이한 서비스 구조
- **실시간 문서 생성**: AI 기반 보고서 자동 생성 및 다운로드

### 📊 **데이터 처리 능력**
- **기업 재무 데이터**: DART, 유가증권시장 데이터 통합
- **기후 시나리오**: IPCC SSP2.6, SSP8.5 시나리오 분석
- **ESG 표준**: TCFD, GRI, KCGS, SASB 등 다중 표준 지원
- **벡터 검색**: 의미론적 유사도를 통한 관련 문서 검색

### 🚀 **사용자 경험**
- **직관적 UI**: 포트폴리오 스타일의 대시보드
- **원클릭 보고서**: AI 기반 자동 보고서 생성
- **다양한 형식**: Word, PDF, HTML 등 다중 형식 지원
- **실시간 피드백**: 생성 과정의 실시간 모니터링

이 프로젝트는 **ESG 분석의 복잡성을 AI로 단순화**하고, **모든 기업이 지속가능한 미래를 위한 의사결정을 내릴 수 있도록** 지원하는 혁신적인 플랫폼입니다.
