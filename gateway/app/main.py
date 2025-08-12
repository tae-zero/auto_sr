from typing import Optional, List
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import Request
import asyncio

from app.router.auth_router import router as auth_router
from app.www.jwt_auth_middleware import AuthMiddleware
from app.domain.discovery.service_discovery import ServiceDiscovery
from app.domain.discovery.service_type import ServiceType
from app.common.utility.constant.settings import Settings
from app.common.utility.factory.response_factory import ResponseFactory
# Gateway는 DB에 직접 접근하지 않음 (MSA 원칙)

if os.getenv("RAILWAY_ENVIRONMENT") != "true":
    load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gateway_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Gateway API 서비스 시작")

    # Settings 초기화 및 앱 state에 등록
    app.state.settings = Settings()
    
    # 서비스 디스커버리 초기화 및 서비스 등록
    app.state.service_discovery = ServiceDiscovery()
    
    # Auth Service 연결 테스트
    # Railway 환경에서는 RAILWAY_AUTH_SERVICE_URL 사용, 로컬에서는 Docker 컨테이너 이름 사용
    auth_service_url = os.getenv("RAILWAY_AUTH_SERVICE_URL")
    if auth_service_url:
        # Railway 환경
        logger.info(f"🚀 Railway 환경에서 Auth Service 연결 시도: {auth_service_url}")
    else:
        # 로컬 Docker 환경 또는 Railway에서 환경변수가 설정되지 않은 경우
        auth_service_url = "http://localhost:8008"  # 로컬 auth-service
        logger.info(f"🚀 로컬 Auth Service 연결 시도: {auth_service_url}")
    
    try:
        import httpx
        # 더 긴 타임아웃과 재시도 로직
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{auth_service_url}/health")
                    if response.status_code == 200:
                        logger.info(f"✅ Auth Service 연결 성공: {auth_service_url}")
                        break
                    else:
                        logger.warning(f"⚠️ Auth Service 응답 이상 (시도 {attempt + 1}/3): {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Auth Service 연결 시도 {attempt + 1}/3 실패: {str(e)}")
                if attempt < 2:  # 마지막 시도가 아니면 잠시 대기
                    await asyncio.sleep(2)
                else:
                    logger.warning(f"⚠️ Auth Service 연결 최종 실패 (서비스는 계속 실행): {str(e)}")
    except Exception as e:
        logger.warning(f"⚠️ Auth Service 연결 테스트 중 오류 (서비스는 계속 실행): {str(e)}")
    
    # 기본 서비스 등록
    app.state.service_discovery.register_service(
        service_name="chatbot-service",
        instances=[{"host": "chatbot-service", "port": 8006, "weight": 1}],
        load_balancer_type="round_robin"
    )
    
    # Auth Service 등록
    app.state.service_discovery.register_service(
        service_name="auth-service",
        instances=[{"host": "auth-service", "port": 8008, "weight": 1}],
        load_balancer_type="round_robin"
    )
    
    yield
    logger.info("🛑 Gateway API 서비스 종료")

app = FastAPI(
    title="Gateway API",
    description="Gateway API for ausikor.com",
    version="0.1.0",
    docs_url="/docs",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 로컬 접근
        "http://127.0.0.1:3000",  # 로컬 IP 접근
        "http://frontend:3000",   # Docker 내부 네트워크
        "https://www.taezero.com",  # 프로덕션 도메인
        "https://taezero.com",      # 프로덕션 도메인 (www 없이)
        "*"  # 개발 환경에서 모든 origin 허용
    ], # 프론트엔드 주소 명시
    allow_credentials=True,  # HttpOnly 쿠키 사용을 위해 필수
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

gateway_router = APIRouter(prefix="/api/v1", tags=["Gateway API"])
gateway_router.include_router(auth_router)
# 필요시: gateway_router.include_router(user_router)
app.include_router(gateway_router)

# 동적 라우팅을 위한 별도 라우터
dynamic_router = APIRouter(prefix="/api/v1", tags=["Dynamic Routing"])
app.include_router(dynamic_router)

# 🪡🪡🪡 파일이 필요한 서비스 목록 (현재는 없음)
FILE_REQUIRED_SERVICES = set()





@gateway_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(
    service: ServiceType, 
    path: str, 
    request: Request
):
    try:
        # app.state에서 service_discovery 가져오기
        service_discovery = request.app.state.service_discovery
        
        # 헤더 전달 (JWT 및 사용자 ID - 미들웨어에서 이미 X-User-Id 헤더가 추가됨)
        headers = dict(request.headers)
        
        response = await service_discovery.request(
            method="GET",
            path=path,
            headers=headers
        )
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in GET proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# 파일 업로드 및 일반 JSON 요청 모두 처리, JWT 적용
@gateway_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(
    service: ServiceType, 
    path: str,
    request: Request,
    file: Optional[UploadFile] = None,
    sheet_names: Optional[List[str]] = Query(None, alias="sheet_name")
):
    try:
        # 디버깅 로그 추가
        logger.info(f"🔍 Gateway POST 요청: service={service}, path={path}")
        logger.info(f"📤 요청 URL: /api/v1/{service}/{path}")
        
        # app.state에서 service_discovery 가져오기
        service_discovery = request.app.state.service_discovery
        
        # 서비스 인스턴스 확인
        instance = service_discovery.get_service_instance(str(service))
        if instance:
            logger.info(f"✅ 서비스 인스턴스 찾음: {instance.host}:{instance.port}")
            logger.info(f"🎯 최종 요청 URL: http://{instance.host}:{instance.port}/{path}")
        else:
            logger.error(f"❌ 서비스 인스턴스를 찾을 수 없음: {service}")
            logger.error(f"🔍 등록된 서비스들: {list(service_discovery.registry.keys())}")
            return JSONResponse(
                content={"detail": f"Service {service} not available"},
                status_code=503
            )
        # 로깅
        logger.info(f"🌈 POST 요청 받음: 서비스={service}, 경로={path}")
        if file:
            logger.info(f"파일명: {file.filename}, 시트 이름: {sheet_names if sheet_names else '없음'}")

        # app.state에서 service_discovery 가져오기
        service_discovery = request.app.state.service_discovery
        
        # 요청 파라미터 초기화
        files = None
        params = None
        body = None
        data = None
        
        # 헤더 전달 (JWT 및 사용자 ID - 미들웨어에서 이미 X-User-Id 헤더가 추가됨)
        headers = dict(request.headers)
        
        # 파일이 필요한 서비스 처리
        if service in FILE_REQUIRED_SERVICES:
            # 파일이 필요한 서비스인 경우
            
            # 서비스 URI가 upload인 경우만 파일 체크
            if "upload" in path and not file:
                raise HTTPException(status_code=400, detail=f"서비스 {service}에는 파일 업로드가 필요합니다.")
            
            # 파일이 제공된 경우 처리
            if file:
                file_content = await file.read()
                files = {'file': (file.filename, file_content, file.content_type)}
                
                # 파일 위치 되돌리기 (다른 코드에서 다시 읽을 수 있도록)
                await file.seek(0)
            
            # 시트 이름이 제공된 경우 처리
            if sheet_names:
                params = {'sheet_name': sheet_names}
        else:
            # 일반 서비스 처리 (body JSON 전달)
            try:
                body = await request.body()
                if not body:
                    # body가 비어있는 경우도 허용
                    logger.info("요청 본문이 비어 있습니다.")
            except Exception as e:
                logger.warning(f"요청 본문 읽기 실패: {str(e)}")
                
        # 서비스에 요청 전달
        response = await service_discovery.request(
            method="POST",
            path=path,
            headers=headers,
            body=body,
            files=files,
            params=params,
            data=data
        )
        
        # 응답 처리 및 반환
        return ResponseFactory.create_response(response)
        
    except HTTPException as he:
        # HTTP 예외는 그대로 반환
        return JSONResponse(
            content={"detail": he.detail},
            status_code=he.status_code
        )
    except Exception as e:
        # 일반 예외는 로깅 후 500 에러 반환
        logger.error(f"POST 요청 처리 중 오류 발생: {str(e)}")
        return JSONResponse(
            content={"detail": f"Gateway error: {str(e)}"},
            status_code=500
        )

# PUT - 일반 동적 라우팅 (JWT 적용)
@gateway_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: ServiceType, path: str, request: Request):
    try:
        # app.state에서 service_discovery 가져오기
        service_discovery = request.app.state.service_discovery
        
        # 헤더 전달 (JWT 및 사용자 ID - 미들웨어에서 이미 X-User-Id 헤더가 추가됨)
        headers = dict(request.headers)
        
        response = await service_discovery.request(
            method="PUT",
            path=path,
            headers=headers,
            body=await request.body()
        )
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in PUT proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# DELETE - 일반 동적 라우팅 (JWT 적용)
@gateway_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: ServiceType, path: str, request: Request):
    try:
        # app.state에서 service_discovery 가져오기
        service_discovery = request.app.state.service_discovery
        
        # 헤더 전달 (JWT 및 사용자 ID - 미들웨어에서 이미 X-User-Id 헤더가 추가됨)
        headers = dict(request.headers)
        
        response = await service_discovery.request(
            method="DELETE",
            path=path,
            headers=headers,
            body=await request.body()
        )
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in DELETE proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# PATCH - 일반 동적 라우팅 (JWT 적용)
@gateway_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: ServiceType, path: str, request: Request):
    try:
        # app.state에서 service_discovery 가져오기
        service_discovery = request.app.state.service_discovery
        
        # 헤더 전달 (JWT 및 사용자 ID - 미들웨어에서 이미 X-User-Id 헤더가 추가됨)
        headers = dict(request.headers)
        
        response = await service_discovery.request(
            method="PATCH",
            path=path,
            headers=headers,
            body=await request.body()
        )
        return ResponseFactory.create_response(response)
    except Exception as e:
        logger.error(f"Error in PATCH proxy: {str(e)}")
        return JSONResponse(
            content={"detail": f"Error processing request: {str(e)}"},
            status_code=500
        )

# ✅ 메인 라우터 등록 (동적 라우팅)
# app.include_router(gateway_router) # 중복된 라우터 등록 제거

# 404 에러 핸들러
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    logger.error(f"404 에러: {request.url}")
    return JSONResponse(
        status_code=404,
        content={"detail": f"요청한 리소스를 찾을 수 없습니다. URL: {request.url}"}
    )

# 기본 루트 경로
@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0"}

# 루트 레벨 헬스 체크
@app.get("/health")
async def health_check_root():
    return {"status": "healthy", "service": "gateway", "path": "root"}

# 데이터베이스 헬스 체크 (auth-service에 위임)
@app.get("/health/db")
async def health_check_db():
    return {
        "status": "healthy",
        "service": "gateway",
        "message": "Database health check delegated to auth-service"
    }

# Gateway는 순수한 라우팅만 담당 (MSA 원칙)


# ✅ 서버 실행
if __name__ == "__main__":
    import uvicorn
    # Railway의 PORT 환경변수 사용, 없으면 8080 기본값
    port = int(os.getenv("PORT", os.getenv("SERVICE_PORT", 8080)))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)