# 🚀 CI/CD 설정 가이드

이 프로젝트는 GitHub Actions + Vercel(Frontend) + Railway(Backend) 조합으로 CI/CD가 구성되어 있습니다.

## 📋 **필요한 GitHub Secrets 설정**

### 1. **Vercel 설정 (Frontend 배포용)**
GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음을 설정하세요:

```bash
VERCEL_TOKEN=your_vercel_token_here
VERCEL_ORG_ID=your_vercel_org_id_here
VERCEL_PROJECT_ID=your_vercel_project_id_here
```

**Vercel 토큰 생성 방법:**
1. [Vercel Dashboard](https://vercel.com/dashboard)에 로그인
2. Settings > Tokens에서 새 토큰 생성
3. 토큰을 복사하여 `VERCEL_TOKEN`에 설정

**Vercel 프로젝트 ID 확인 방법:**
1. Vercel 프로젝트 페이지에서 Settings 탭
2. General 섹션에서 Project ID 확인

### 2. **Railway 설정 (Backend 배포용)**
```bash
RAILWAY_TOKEN=your_railway_token_here
```

**Railway 토큰 생성 방법:**
1. [Railway Dashboard](https://railway.app/dashboard)에 로그인
2. Settings > Tokens에서 새 토큰 생성
3. 토큰을 복사하여 `RAILWAY_TOKEN`에 설정

## 🔄 **CI/CD 파이프라인 동작 방식**

### **Frontend (Next.js)**
1. **코드 푸시** → GitHub Actions 트리거
2. **의존성 설치** → `npm ci`
3. **Lint & Type Check** → 코드 품질 검사
4. **빌드** → `npm run build`
5. **배포** → Vercel에 자동 배포 (main 브랜치만)

### **Backend Services (FastAPI)**
1. **코드 푸시** → GitHub Actions 트리거
2. **의존성 설치** → `pip install -r requirements.txt`
3. **테스트 실행** → pytest (설정된 경우)
4. **Docker 이미지 빌드** → GitHub Container Registry에 푸시
5. **배포** → Railway에 수동 배포 (각 서비스별 개별 프로젝트)

### **통합 테스트**
1. **모든 서비스 빌드 완료** 후 실행
2. **Docker Compose**로 전체 시스템 시작
3. **Health Check** 확인
4. **서비스 정리**

## 🐳 **Docker 이미지 관리**

### **GitHub Container Registry**
- 모든 서비스의 Docker 이미지가 자동으로 빌드되어 저장
- 태그: `ghcr.io/username/repo-name-service:branch-commit`
- 캐시를 통한 빠른 빌드

### **이미지 태그 규칙**
- `main` 브랜치: `latest`, `main-commit-hash`
- `develop` 브랜치: `develop-commit-hash`
- 태그: `v1.0.0`, `v1.0`

## 📁 **파일 구조**

```
.github/
├── workflows/
│   ├── ci-cd.yml          # 메인 CI/CD 파이프라인
│   ├── docker-build.yml   # Docker 빌드 전용
│   └── test.yml           # 테스트 및 코드 품질 검사
├── frontend/
│   ├── Dockerfile         # Frontend Docker 설정
│   ├── railway.json       # Railway 배포 설정
│   └── vercel.json        # Vercel 배포 설정
├── gateway/
│   ├── Dockerfile         # Gateway Docker 설정
│   └── railway.json       # Gateway Railway 설정
├── service/
│   ├── auth-service/
│   │   ├── Dockerfile     # Auth Service Docker 설정
│   │   └── railway.json   # Auth Service Railway 설정
│   └── chatbot-service/
│       ├── Dockerfile     # Chatbot Service Docker 설정
│       └── railway.json   # Chatbot Service Railway 설정
├── scripts/
│   ├── deploy-status.sh   # 배포 상태 확인 스크립트
│   └── test-services.sh   # 서비스 테스트 스크립트
└── Makefile               # CI/CD 및 개발 명령어
```

## 🚀 **배포 환경**

### **Frontend**
- **개발**: `develop` 브랜치 푸시 시 Vercel Preview 배포
- **프로덕션**: `main` 브랜치 푸시 시 Vercel Production 배포

### **Backend**
- **개발**: `develop` 브랜치 푸시 시 Railway 개발 환경 배포
- **프로덕션**: `main` 브랜치 푸시 시 Railway 프로덕션 환경 배포

## 🔧 **로컬 개발 환경**

```bash
# 전체 시스템 시작
make up

# 특정 서비스만 시작
make up-frontend
make up-gateway
make up-chatbot-service

# 로그 확인
make logs
make logs-frontend

# 시스템 정리
make down

# 🧪 테스트 실행
make test-local      # 로컬 환경에서 전체 테스트
make test-services   # 실행 중인 서비스 테스트
```

## 📊 **모니터링 및 로그**

### **GitHub Actions**
- Actions 탭에서 모든 워크플로우 실행 상태 확인
- 실패한 단계의 상세 로그 확인

### **Vercel**
- Dashboard에서 배포 상태 및 성능 메트릭 확인
- Preview 배포 URL로 테스트

### **Railway**
- Dashboard에서 서비스 상태 및 로그 확인
- 자동 스케일링 및 헬스체크 모니터링

## 🚨 **문제 해결**

### **Frontend 배포 실패**
1. Vercel 토큰이 유효한지 확인
2. 프로젝트 ID가 올바른지 확인
3. 빌드 로그에서 오류 확인

### **Backend 배포 실패**
1. Railway 토큰이 유효한지 확인
2. Docker 이미지 빌드 성공 여부 확인
3. Railway 로그에서 오류 확인

### **Docker 빌드 실패**
1. Dockerfile 문법 오류 확인
2. 의존성 설치 문제 확인
3. GitHub Container Registry 권한 확인

## 📚 **추가 리소스**

- [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
- [Vercel 배포 가이드](https://vercel.com/docs/deployments)
- [Railway 배포 가이드](https://docs.railway.app/deploy/deployments)
- [Docker GitHub Actions](https://docs.docker.com/ci-cd/github-actions/)
- [Railway 배포 상세 가이드](./RAILWAY-DEPLOYMENT.md)
