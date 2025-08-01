from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio
import logging
import time
from contextlib import asynccontextmanager

# 설정 및 서비스 디스커버리 import
from app.common.config import settings, DEFAULT_SERVICE_REGISTRY
from app.domain.discovery.service_discovery import ServiceDiscovery
from app.www.proxy import ProxyService


# 로깅 설정
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# 서비스 디스커버리 및 프록시 서비스 초기화
service_discovery = ServiceDiscovery()
proxy_service = ProxyService(service_discovery, timeout=settings.REQUEST_TIMEOUT)

# 기본 서비스 등록
for service_name, service_config in DEFAULT_SERVICE_REGISTRY.items():
    service_discovery.register_service(
        service_name=service_name,
        instances=service_config["instances"],
        load_balancer_type=service_config["load_balancer"]
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    logger.info("Gateway starting up...")
    
    # 주기적 헬스 체크 태스크 시작
    health_check_task = asyncio.create_task(periodic_health_check())
    
    yield
    
    # 정리 작업
    health_check_task.cancel()
    await proxy_service.close()
    logger.info("Gateway shutting down...")

async def periodic_health_check():
    """주기적 헬스 체크 수행"""
    while True:
        try:
            await service_discovery.health_check_all_services()
            await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
            await asyncio.sleep(settings.HEALTH_CHECK_INTERVAL)

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="MSA Gateway",
    description="""
    ## 마이크로서비스 아키텍처 Gateway
    
    Proxy 패턴을 이용한 서비스 디스커버리와 로드 밸런싱 기능을 제공하는 API Gateway입니다.
    
    ### 주요 기능
    - **서비스 디스커버리**: 등록된 서비스들의 인스턴스를 관리하고 동적으로 선택
    - **로드 밸런싱**: Round Robin, Least Connections, Random, Weighted Round Robin 지원
    - **헬스 체크**: 주기적인 서비스 인스턴스 상태 확인
    - **프록시 라우팅**: 모든 요청을 적절한 서비스로 전달
    - **모니터링**: 서비스 상태 및 응답 시간 모니터링
    
    ### 사용법
    1. Gateway 상태 확인: `GET /`
    2. 서비스 목록 조회: `GET /services`
    3. 프록시 요청: `GET /{service_name}/{path}`
    
    ### 예시
    - `GET /user-service/users` → user-service의 /users 엔드포인트로 전달
    - `POST /order-service/orders` → order-service의 /orders 엔드포인트로 전달
    """,
    version="1.0.0",
    contact={
        "name": "MSA Gateway Team",
        "email": "gateway@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "개발 서버"
        },
        {
            "url": "https://gateway.example.com",
            "description": "프로덕션 서버"
        }
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

@app.get("/", 
    summary="Gateway 상태 확인",
    description="MSA Gateway의 현재 상태와 등록된 서비스 목록을 확인합니다.",
    response_description="Gateway 상태 정보",
    tags=["Gateway 관리"]
)
async def root():
    """Gateway 상태 확인"""
    return {
        "message": "MSA Gateway is running",
        "services": list(service_discovery.registry.keys()),
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@app.get("/health",
    summary="Gateway 헬스 체크",
    description="MSA Gateway의 헬스 상태를 확인합니다. 모니터링 시스템에서 주기적으로 호출하여 Gateway의 가용성을 확인할 수 있습니다.",
    response_description="Gateway 헬스 상태",
    tags=["Gateway 관리"]
)
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "gateway": "running"}

@app.get("/services",
    summary="등록된 서비스 목록 조회",
    description="서비스 디스커버리에 등록된 모든 서비스의 상태 정보를 조회합니다. 각 서비스의 인스턴스 수, 헬스 상태, 로드 밸런서 타입 등의 정보를 확인할 수 있습니다.",
    response_description="서비스 목록 및 상태 정보",
    tags=["서비스 관리"]
)
async def list_services():
    """등록된 서비스 목록 조회"""
    return service_discovery.get_all_services_status()

@app.get("/services/{service_name}/health",
    summary="특정 서비스 헬스 체크",
    description="지정된 서비스의 헬스 상태를 확인합니다. 해당 서비스의 인스턴스 중 하나를 선택하여 헬스 체크를 수행하고 결과를 반환합니다.",
    response_description="서비스 헬스 상태 정보",
    tags=["서비스 관리"]
)
async def service_health_check(service_name: str):
    """특정 서비스 헬스 체크"""
    return await proxy_service.health_check_service(service_name)

@app.api_route("/{service_name}/{path:path}", 
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    summary="서비스 프록시 요청",
    description="""
    모든 서비스 요청을 프록시를 통해 해당 서비스로 전달합니다.
    
    ### 동작 방식
    1. 서비스 디스커버리를 통해 적절한 서비스 인스턴스 선택
    2. 로드 밸런싱 알고리즘 적용 (Round Robin, Least Connections 등)
    3. 요청을 선택된 인스턴스로 전달
    4. 응답을 클라이언트에게 반환
    
    ### 지원하는 HTTP 메서드
    - GET: 데이터 조회
    - POST: 데이터 생성
    - PUT: 데이터 수정
    - DELETE: 데이터 삭제
    - PATCH: 부분 데이터 수정
    
    ### 예시
    - `GET /user-service/users` → user-service의 /users 엔드포인트로 전달
    - `POST /order-service/orders` → order-service의 /orders 엔드포인트로 전달
    - `PUT /product-service/products/123` → product-service의 /products/123 엔드포인트로 전달
    """,
    response_description="프록시된 서비스의 응답",
    tags=["프록시"]
)
async def proxy_request(
    service_name: str,
    path: str,
    request: Request
):
    """모든 서비스 요청을 프록시로 전달"""
    
    try:
        # 프록시 서비스를 통해 요청 처리
        return await proxy_service.handle_request(request, service_name, path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# 서비스별 라우터 등록
from app.router import user_router

# 서비스별 라우터를 메인 앱에 포함
app.include_router(user_router.router, prefix="/api/v1", tags=["user"])

# if __name__ == "__main__":
#     import uvicorn
#     import os

#     port = int(os.environ.get("PORT", 8000))  # Railway 환경에서 포트 자동 할당됨

#     uvicorn.run(
#         "app.main:app",  # 문자열로 경로 지정 시 reload 가능
#         host="0.0.0.0",
#         port=port,
#         reload=False
#     )
