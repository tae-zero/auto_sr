# Service 디렉토리 환경변수 설정 가이드

이 디렉토리는 ESG MATE MSA 프로젝트의 모든 마이크로서비스를 포함합니다.

## 🏗️ 서비스 구조

```
service/
├── auth-service/           # 인증 서비스 (포트: 8008)
├── chatbot-service/        # 챗봇 서비스 (포트: 8001)
├── gri-service/           # GRI 보고서 서비스 (포트: 8006)
├── materiality-service/   # Materiality 분석 서비스 (포트: 8007)
├── rag-service/           # RAG 서비스 (포트: 8002)
├── tcfd-service/          # TCFD 서비스 (포트: 8005)
└── tcfdreport-service/    # TCFD 보고서 서비스 (포트: 8004)
```

## 🔐 환경변수 설정

각 서비스는 자체 `.env` 파일을 가집니다. `env.example`을 복사하여 `.env`로 만들고 실제 값으로 수정하세요.

### **1. Auth Service**
```bash
cd service/auth-service
cp env.example .env
nano .env
```

**필수 환경변수:**
- `JWT_SECRET_KEY`: JWT 토큰 서명을 위한 시크릿 키
- `DATABASE_URL`: PostgreSQL 데이터베이스 연결 문자열
- `SERVICE_PORT`: 서비스 포트 (기본값: 8008)

### **2. TCFD Service**
```bash
cd service/tcfd-service
cp env.example .env
nano .env
```

**필수 환경변수:**
- `JWT_SECRET_KEY`: JWT 토큰 서명을 위한 시크릿 키
- `DATABASE_URL`: PostgreSQL 데이터베이스 연결 문자열
- `SERVICE_PORT`: 서비스 포트 (기본값: 8005)

### **3. TCFD Report Service**
```bash
cd service/tcfdreport-service
cp env.example .env
nano .env
```

**필수 환경변수:**
- `JWT_SECRET_KEY`: JWT 토큰 서명을 위한 시크릿 키
- `DATABASE_URL`: PostgreSQL 데이터베이스 연결 문자열
- `SERVICE_PORT`: 서비스 포트 (기본값: 8004)
- `OPENAI_API_KEY`: OpenAI API 키 (AI 기능 사용 시)

### **4. Chatbot Service**
```bash
cd service/chatbot-service
cp env.example .env
nano .env
```

**필수 환경변수:**
- `JWT_SECRET_KEY`: JWT 토큰 서명을 위한 시크릿 키
- `SERVICE_PORT`: 서비스 포트 (기본값: 8001)

### **5. GRI Service**
```bash
cd service/gri-service
cp env.example .env
nano .env
```

**필수 환경변수:**
- `DATABASE_URL`: PostgreSQL 데이터베이스 연결 문자열
- `SECRET_KEY`: 보안을 위한 시크릿 키
- `SERVICE_PORT`: 서비스 포트 (기본값: 8006)

### **6. Materiality Service**
```bash
cd service/materiality-service
cp env.example .env
nano .env
```

**필수 환경변수:**
- `DATABASE_URL`: PostgreSQL 데이터베이스 연결 문자열
- `SECRET_KEY`: 보안을 위한 시크릿 키
- `SERVICE_PORT`: 서비스 포트 (기본값: 8007)

### **7. RAG Service**
```bash
cd service/rag-service
cp env.example .env
nano .env
```

**필수 환경변수:**
- `OPENAI_API_KEY`: OpenAI API 키
- `SERVICE_PORT`: 서비스 포트 (기본값: 8002)

## 🌍 환경별 설정

### **🐳 Docker 환경**
```bash
# 각 서비스 디렉토리에서
cp env.example .env

# .env 파일 편집
nano .env
```

### **🚂 Railway 환경**
Railway 대시보드에서 각 서비스의 Variables 탭에 환경변수를 설정하세요.

**공통 환경변수:**
```
RAILWAY_ENVIRONMENT=production
```

**JWT 관련 서비스 (Auth, TCFD, TCFD Report, Chatbot):**
```
JWT_SECRET_KEY=your-super-secret-jwt-key-here
```

**데이터베이스 사용 서비스:**
```
DATABASE_URL=postgresql://postgres:password@host:port/database
```

### **🔧 개발 환경**
```bash
# 각 서비스 디렉토리에서
cp env.example .env

# 개발용 값으로 수정
nano .env
```

## ⚠️ 주의사항

1. **JWT_SECRET_KEY**: 모든 JWT 관련 서비스에서 동일한 값이어야 합니다.
2. **DATABASE_URL**: 데이터베이스를 사용하는 서비스에서 설정해야 합니다.
3. **포트 충돌**: 각 서비스는 고유한 포트를 사용해야 합니다.
4. **환경변수 우선순위**: `SERVICE_PORT` > `PORT` > 기본값

## 🚀 서비스 실행

### **개별 서비스 실행**
```bash
cd service/[service-name]
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port [PORT]
```

### **Docker Compose로 실행**
```bash
# 루트 디렉토리에서
docker-compose up -d
```

## 📊 헬스 체크

각 서비스는 `/health` 엔드포인트를 제공합니다:

```bash
curl http://localhost:[PORT]/health
```

## 🔍 로그 확인

```bash
# Docker Compose 로그
docker-compose logs -f [service-name]

# 개별 서비스 로그
docker logs [container-name]
```
