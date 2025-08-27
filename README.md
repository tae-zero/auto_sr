# ESG Mate - AI 기반 ESG 분석 및 보고서 생성 플랫폼

## 🚀 주요 기능

### 🤖 AI 기반 TCFD 보고서 생성
- **OpenAI GPT-4o-mini**: 글로벌 최고 수준의 언어 모델로 정확한 사실 기반 응답
- **KoAlpaca/RoLA**: 한국어 특화 자연스러운 표현과 한국 기업 문화 이해
- **TCFD 프레임워크**: 거버넌스, 전략, 위험관리, 지표 및 목표의 4개 핵심 영역 지원

### 📄 다운로드 기능 (신규 추가!)
- **Word 문서 (.docx)**: 초안과 윤문을 포함한 전문적인 TCFD 보고서
- **PDF 문서**: 인쇄 및 공유에 최적화된 형식
- **회사별 맞춤**: 회사명과 생성일시가 포함된 개인화된 문서
- **AI 모델별 구분**: OpenAI와 KoAlpaca 모델의 결과를 각각 다운로드

### 📊 데이터 분석 및 시각화
- **기후 시나리오 분석**: SSP2.6, SSP8.5 시나리오별 기후 변화 예측
- **재무 데이터 대시보드**: 종합적인 재무 상태 및 성과 분석
- **ESG 지표 추적**: 지속가능성 성과 모니터링

### 🔐 보안 및 인증
- **JWT 기반 인증**: 안전한 사용자 인증 및 세션 관리
- **회사별 데이터 격리**: 사용자별 데이터 접근 권한 관리

## 🏗️ 아키텍처

### Frontend (Next.js)
- **React 19 + TypeScript**: 최신 프론트엔드 기술 스택
- **Tailwind CSS**: 반응형 및 모던한 UI/UX
- **Zustand**: 효율적인 상태 관리

### Backend (FastAPI)
- **MSA 구조**: 각 도메인별 독립적인 서비스
- **TCFD Report Service**: AI 기반 보고서 생성 및 다운로드
- **LLM Service**: OpenAI 및 Hugging Face 모델 통합
- **Gateway**: 통합 API 게이트웨이

### AI/ML
- **LangChain**: RAG(Retrieval-Augmented Generation) 구현
- **Vector Database**: ChromaDB를 활용한 문서 검색
- **Multi-Model Support**: 다양한 AI 모델 지원

## 📥 다운로드 기능 사용법

### 1. TCFD 보고서 생성
1. TCFD 프레임워크 탭에서 회사 정보 및 ESG 데이터 입력
2. AI 모델 선택 (OpenAI 또는 KoAlpaca)
3. "AI 보고서 생성 시작" 버튼 클릭

### 2. 문서 다운로드
- **Word 다운로드**: 📄 버튼 클릭으로 .docx 파일 다운로드
- **PDF 다운로드**: 📕 버튼 클릭으로 PDF 파일 다운로드
- **파일명 형식**: `{회사명}_TCFD_보고서_{날짜시간}.{확장자}`

### 3. 다운로드 내용
- 회사명 및 생성일시
- AI 생성 초안 (TCFD 프레임워크 기반)
- 윤문된 최종 텍스트
- 전문적인 문서 포맷팅

## 🛠️ 설치 및 실행

### Prerequisites
- Docker & Docker Compose
- Node.js 20.x
- Python 3.9+

### Quick Start
```bash
# 1. 저장소 클론
git clone <repository-url>
cd auto_sr

# 2. 환경 변수 설정
cp env.example .env
# .env 파일 편집하여 필요한 값 설정

# 3. Docker Compose로 서비스 실행
docker-compose up -d

# 4. 프론트엔드 접속
# http://localhost:3001
```

## 🔧 환경 변수

### 필수 설정
```bash
# 데이터베이스
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# JWT 인증
JWT_SECRET_KEY=your-secret-key

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Hugging Face
HF_API_TOKEN=your-huggingface-token
```

## 📚 API 문서

### TCFD Report Service
- `POST /api/v1/tcfdreport/download/word`: Word 문서 다운로드
- `POST /api/v1/tcfdreport/download/pdf`: PDF 다운로드
- `POST /api/v1/tcfdreport/inputs`: TCFD 입력 데이터 생성
- `GET /api/v1/tcfdreport/inputs/{company_name}`: 회사별 TCFD 데이터 조회

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이나 제안사항이 있으시면 이슈를 생성해 주세요.

---

**ESG Mate** - 지속가능한 미래를 위한 AI 기반 ESG 분석 플랫폼 🚀
