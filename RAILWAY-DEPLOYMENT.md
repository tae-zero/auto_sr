# 🚂 Railway 배포 가이드

Railway에서는 각 마이크로서비스를 개별 프로젝트로 배포해야 합니다. 이 가이드는 각 서비스를 Railway에 배포하는 방법을 설명합니다.

## 📋 **Railway 배포 단계**

### **1. Gateway 서비스 배포**

1. **Railway 프로젝트 생성**
   - [Railway Dashboard](https://railway.app/dashboard)에서 "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - GitHub 저장소 선택

2. **서비스 추가**
   - "Add Service" → "GitHub Repo" 선택
   - **서비스 경로**: `gateway`
   - **프로젝트 이름**: `gateway-service`

3. **환경변수 설정**
   ```bash
   PORT=8080
   PYTHONUNBUFFERED=1
   LOG_LEVEL=INFO
   GATEWAY_HOST=0.0.0.0
   GATEWAY_PORT=8080
   GATEWAY_RELOAD=false
   SERVICE_DISCOVERY_TYPE=static
   LOAD_BALANCER_TYPE=round_robin
   REQUEST_TIMEOUT=30
   HEALTH_CHECK_INTERVAL=30
   CORS_ORIGINS=["*"]
   CORS_ALLOW_CREDENTIALS=true
   CORS_ALLOW_METHODS=["*"]
   CORS_ALLOW_HEADERS=["*"]
   INIT_DATABASE=true
   DATABASE_URL=your_postgresql_connection_string
   ```

4. **배포 확인**
   - 배포 완료 후 제공되는 URL로 접속
   - `/health` 엔드포인트로 헬스체크 확인

### **2. Auth Service 배포**

1. **새 프로젝트 생성 또는 기존 프로젝트에 서비스 추가**
   - "New Project" → "Deploy from GitHub repo"
   - 또는 기존 프로젝트에서 "Add Service"

2. **서비스 설정**
   - **서비스 경로**: `service/auth-service`
   - **프로젝트 이름**: `auth-service`

3. **환경변수 설정**
   ```bash
   PORT=8008
   PYTHONUNBUFFERED=1
   LOG_LEVEL=INFO
   SERVICE_HOST=0.0.0.0
   SERVICE_PORT=8008
   INIT_DATABASE=true
   DATABASE_URL=your_postgresql_connection_string
   ```

4. **배포 확인**
   - `/health` 엔드포인트로 헬스체크 확인

### **3. Chatbot Service 배포**

1. **서비스 추가**
   - 기존 프로젝트에 "Add Service" 또는 새 프로젝트 생성
   - **서비스 경로**: `service/chatbot-service`
   - **프로젝트 이름**: `chatbot-service`

2. **환경변수 설정**
   ```bash
   PORT=8006
   PYTHONUNBUFFERED=1
   LOG_LEVEL=INFO
   SERVICE_HOST=0.0.0.0
   SERVICE_PORT=8006
   ```

3. **배포 확인**
   - `/health` 엔드포인트로 헬스체크 확인

## 🔧 **Railway 프로젝트 구조**

```
Railway Dashboard
├── gateway-service (프로젝트)
│   └── gateway (서비스)
├── auth-service (프로젝트)
│   └── auth-service (서비스)
└── chatbot-service (프로젝트)
    └── chatbot-service (서비스)
```

## 📊 **배포 후 확인사항**

### **1. 서비스 상태 확인**
- Railway Dashboard에서 각 서비스의 상태 확인
- 로그에서 오류 메시지 확인
- 헬스체크 엔드포인트 응답 확인

### **2. 서비스 간 연결**
- Gateway에서 다른 서비스들의 URL 업데이트
- CORS 설정 확인
- 네트워크 연결 테스트

### **3. 환경변수 확인**
- 각 서비스의 필수 환경변수 설정 확인
- 데이터베이스 연결 문자열 확인
- 포트 설정 확인

## 🚨 **문제 해결**

### **Dockerfile을 찾을 수 없음**
- **원인**: 서비스 경로가 잘못 설정됨
- **해결**: Railway에서 서비스 경로를 정확히 지정
  - Gateway: `gateway`
  - Auth Service: `service/auth-service`
  - Chatbot Service: `service/chatbot-service`

### **포트 충돌**
- **원인**: 여러 서비스가 같은 포트 사용
- **해결**: Railway의 PORT 환경변수 사용 (자동 할당)

### **의존성 설치 실패**
- **원인**: requirements.txt 경로 문제
- **해결**: 서비스 경로가 올바른지 확인

### **데이터베이스 연결 실패**
- **원인**: DATABASE_URL 환경변수 누락
- **해결**: Railway PostgreSQL 서비스 추가 후 연결 문자열 설정

## 🔄 **자동 배포 설정**

### **GitHub 연동**
1. Railway 프로젝트에서 "Settings" → "GitHub"
2. "Connect GitHub" 클릭
3. 저장소 및 브랜치 선택
4. 자동 배포 활성화

### **배포 트리거**
- `main` 브랜치 푸시 시 자동 배포
- `develop` 브랜치 푸시 시 자동 배포 (선택사항)

## 📚 **추가 리소스**

- [Railway 공식 문서](https://docs.railway.app/)
- [Railway GitHub 연동](https://docs.railway.app/deploy/deployments)
- [Railway 환경변수 설정](https://docs.railway.app/develop/variables)
- [Railway PostgreSQL](https://docs.railway.app/databases/postgresql)

## 💡 **팁**

1. **서비스별 개별 프로젝트**: 각 마이크로서비스를 별도 프로젝트로 관리하면 독립적인 배포와 스케일링이 가능합니다.

2. **환경변수 관리**: 민감한 정보는 Railway의 환경변수로 관리하고, 코드에 하드코딩하지 마세요.

3. **모니터링**: Railway Dashboard에서 각 서비스의 로그와 메트릭을 모니터링하세요.

4. **백업**: 중요한 데이터는 정기적으로 백업하고, Railway의 백업 기능을 활용하세요.
