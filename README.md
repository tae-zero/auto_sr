# ESG MATE MSA 프로젝트

ESG 관리 플랫폼을 위한 마이크로서비스 아키텍처 프로젝트입니다.

## 🚀 빠른 시작

### 1. 환경변수 설정

프로젝트를 실행하기 전에 환경변수를 설정해야 합니다.

#### 루트 환경변수 설정
```bash
# .env.example을 .env로 복사
cp env.example .env

# .env 파일을 편집하여 실제 값으로 수정
nano .env
```

#### Frontend 환경변수 설정
```bash
# frontend/env.example을 .env.local로 복사
cp frontend/env.example frontend/.env.local

# .env.local 파일을 편집하여 실제 값으로 수정
nano frontend/.env.local
```

#### Gateway 환경변수 설정
```bash
# gateway/env.example을 .env로 복사
cp gateway/env.example gateway/.env

# .env 파일을 편집하여 실제 값으로 수정
nano gateway/.env
```

### 2. Docker Compose로 실행
```bash
# 모든 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 3. 개발 모드로 실행
```bash
# Frontend 개발 서버
cd frontend && npm run dev

# Gateway 개발 서버
cd gateway && uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## 🌍 환경별 배포 가이드

### 🐳 Docker 환경

#### 환경변수 설정
```bash
# .env 파일 생성
cp env.example .env

# 필수 환경변수 설정
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
JWT_SECRET_KEY=your-super-secret-jwt-key-here
RAILWAY_ENVIRONMENT=false
```

#### 실행
```bash
docker-compose up -d
```

### 🚂 Railway 환경

#### 환경변수 설정
Railway 대시보드에서 각 서비스의 Variables 탭에 다음 환경변수를 설정하세요:

**Gateway 서비스:**
```
RAILWAY_ENVIRONMENT=production
JWT_SECRET_KEY=your-super-secret-jwt-key-here
DATABASE_URL=postgresql://postgres:password@host:port/database
RAILWAY_AUTH_SERVICE_URL=https://auth-service-production.up.railway.app
RAILWAY_TCFD_SERVICE_URL=https://tcfd-service-production.up.railway.app
RAILWAY_TCFD_REPORT_SERVICE_URL=https://tcfdreport-service-production.up.railway.app
```

**Auth Service:**
```
JWT_SECRET_KEY=your-super-secret-jwt-key-here
DATABASE_URL=postgresql://postgres:password@host:port/database
```

**TCFD Service:**
```
JWT_SECRET_KEY=your-super-secret-jwt-key-here
DATABASE_URL=postgresql://postgres:password@host:port/database
```

**TCFD Report Service:**
```
JWT_SECRET_KEY=your-super-secret-jwt-key-here
DATABASE_URL=postgresql://postgres:password@host:port/database
```

#### 배포
```bash
# Railway CLI로 배포
railway up
```

### ☁️ Vercel 환경

#### 환경변수 설정
Vercel 대시보드에서 프로젝트의 Environment Variables 탭에 다음 환경변수를 설정하세요:

**Production 환경:**
```
NEXT_PUBLIC_GATEWAY_URL=https://your-gateway.up.railway.app
NEXT_PUBLIC_API_URL=https://your-gateway.up.railway.app/api
NEXT_PUBLIC_TCFD_SERVICE_URL=https://tcfd-service-production.up.railway.app
NEXT_PUBLIC_AUTH_SERVICE_URL=https://auth-service-production.up.railway.app
```

**Preview 환경:**
```
NEXT_PUBLIC_GATEWAY_URL=https://your-gateway-staging.up.railway.app
NEXT_PUBLIC_API_URL=https://your-gateway-staging.up.railway.app/api
NEXT_PUBLIC_TCFD_SERVICE_URL=https://tcfd-service-staging.up.railway.app
NEXT_PUBLIC_AUTH_SERVICE_URL=https://auth-service-staging.up.railway.app
```

#### 배포
```bash
# Vercel CLI로 배포
vercel --prod
```

## 🔐 환경변수 목록

### 필수 환경변수
- `DATABASE_URL`: PostgreSQL 데이터베이스 연결 문자열
- `JWT_SECRET_KEY`: JWT 토큰 서명을 위한 시크릿 키
- `RAILWAY_ENVIRONMENT`: 배포 환경 구분 (false/production)

### 선택적 환경변수
- `OPENAI_API_KEY`: OpenAI API 키 (AI 기능 사용 시)
- `LOG_LEVEL`: 로깅 레벨 (INFO/DEBUG/ERROR)
- `GATEWAY_PORT`: Gateway 서비스 포트
- `FRONTEND_PORT`: Frontend 서비스 포트

## 📁 프로젝트 구조

```
esg_mate/
├── frontend/                 # Next.js Frontend
├── gateway/                  # FastAPI Gateway
├── service/                  # Microservices
│   ├── auth-service/        # 인증 서비스
│   ├── tcfd-service/        # TCFD 서비스
│   ├── tcfdreport-service/  # TCFD 보고서 서비스
│   ├── chatbot-service/     # 챗봇 서비스
│   ├── gri-service/         # GRI 서비스
│   └── materiality-service/ # Materiality 서비스
├── docker-compose.yml       # Docker Compose 설정
├── env.example              # 환경변수 예시
└── README.md               # 프로젝트 문서
```

## 🛠️ 개발 도구

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL
- **Cache**: Redis
- **Container**: Docker, Docker Compose
- **Deployment**: Railway, Vercel

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
