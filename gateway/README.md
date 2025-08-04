# MSA Gateway

FastAPI 기반의 마이크로서비스 아키텍처 Gateway입니다. Proxy 패턴을 이용한 서비스 디스커버리와 로드 밸런싱 기능을 제공합니다.

## 주요 기능

- **서비스 디스커버리**: 등록된 서비스들의 인스턴스를 관리하고 동적으로 선택
- **로드 밸런싱**: Round Robin, Least Connections, Random, Weighted Round Robin 지원
- **헬스 체크**: 주기적인 서비스 인스턴스 상태 확인
- **프록시 라우팅**: 모든 요청을 적절한 서비스로 전달
- **CORS 지원**: 크로스 오리진 요청 처리
- **모니터링**: 서비스 상태 및 응답 시간 모니터링

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 설정

```bash
cp env.example .env
# .env 파일을 편집하여 필요한 설정을 변경
```

### 3. Gateway 실행

```bash
python -m app.main
```

또는

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## API 엔드포인트

### Gateway 관리

- `GET /` - Gateway 상태 확인
- `GET /health` - Gateway 헬스 체크
- `GET /services` - 등록된 서비스 목록 조회
- `GET /services/{service_name}/health` - 특정 서비스 헬스 체크

### 서비스 프록시

- `/{service_name}/{path}` - 모든 HTTP 메서드 지원
  - 예: `GET /user-service/users` → user-service의 /users 엔드포인트로 전달
  - 예: `POST /order-service/orders` → order-service의 /orders 엔드포인트로 전달

## 서비스 등록

현재는 정적 설정을 통해 서비스를 등록합니다. `app/common/config.py`의 `DEFAULT_SERVICE_REGISTRY`를 수정하여 서비스를 추가/수정할 수 있습니다.

```python
DEFAULT_SERVICE_REGISTRY = {
    "user-service": {
        "instances": [
            {"host": "localhost", "port": 8001, "health": True, "weight": 1},
            {"host": "localhost", "port": 8002, "health": True, "weight": 1}
        ],
        "load_balancer": "round_robin",
        "current_index": 0,
        "health_check_path": "/health"
    }
}
```

## 로드 밸런싱 전략

- **round_robin**: 라운드 로빈 방식 (기본값)
- **least_connections**: 최소 연결 수 기준
- **random**: 랜덤 선택
- **weighted_round_robin**: 가중 라운드 로빈

## 헬스 체크

Gateway는 설정된 간격(기본 30초)으로 모든 서비스 인스턴스의 헬스 체크를 수행합니다. 헬스 체크에 실패한 인스턴스는 로드 밸런싱에서 제외됩니다.

## 모니터링

각 요청에 대해 다음 정보가 헤더에 추가됩니다:

- `X-Gateway-Service`: 대상 서비스명
- `X-Gateway-Instance`: 선택된 인스턴스 정보
- `X-Gateway-Response-Time`: 응답 시간

## 개발 환경 설정

### 1. 가상환경 생성

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 개발 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 테스트 서비스 실행

Gateway를 테스트하기 위해 간단한 테스트 서비스를 실행할 수 있습니다:

```bash
# user-service (포트 8001)
python -c "
from fastapi import FastAPI
import uvicorn
app = FastAPI()
@app.get('/health') 
def health(): return {'status': 'healthy'}
@app.get('/users') 
def users(): return {'users': ['user1', 'user2']}
uvicorn.run(app, host='0.0.0.0', port=8001)
"
```

## 프로덕션 배포

### Docker 사용

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 환경 변수

프로덕션 환경에서는 다음 환경 변수를 설정하세요:

- `GATEWAY_HOST`: Gateway 호스트 (기본값: 0.0.0.0)
- `GATEWAY_PORT`: Gateway 포트 (기본값: 8080)
- `REQUEST_TIMEOUT`: 요청 타임아웃 (기본값: 30)
- `HEALTH_CHECK_INTERVAL`: 헬스 체크 간격 (기본값: 30)
- `LOG_LEVEL`: 로그 레벨 (기본값: INFO)

## 아키텍처

```
Gateway
├── Service Discovery (서비스 디스커버리)
│   ├── Service Registry (서비스 레지스트리)
│   ├── Load Balancer (로드 밸런서)
│   └── Health Checker (헬스 체커)
├── Proxy Service (프록시 서비스)
│   ├── Request Forwarding (요청 전달)
│   ├── Response Handling (응답 처리)
│   └── Error Handling (에러 처리)
└── API Gateway (API 게이트웨이)
    ├── Routing (라우팅)
    ├── CORS (크로스 오리진)
    └── Monitoring (모니터링)
```

## 확장 가능한 기능

- Consul/Eureka 기반 동적 서비스 디스커버리
- 인증/인가 미들웨어
- 요청/응답 변환
- API 버전 관리
- 서킷 브레이커 패턴
- 메트릭 수집 (Prometheus)
- 로그 집계 (ELK Stack) 