from typing import Optional, List
from fastapi import APIRouter, FastAPI, Request, UploadFile, File, Query, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging
import sys
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import Request

from app.router.auth_router import router as auth_router
from app.www.jwt_auth_middleware import AuthMiddleware
from app.domain.discovery.service_discovery import ServiceDiscovery
from app.domain.discovery.service_type import ServiceType
from app.common.utility.constant.settings import Settings
from app.common.utility.factory.response_factory import ResponseFactory
from app.common.database.database import get_db, create_tables, test_connection
from app.domain.auth.service.signup_service import SignupService

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

    # Railway PostgreSQL 연결 대기 (로컬 PostgreSQL 대기 제거)
    import asyncio
    await asyncio.sleep(2)

    # Railway 데이터베이스 연결 테스트 (재시도 로직 포함)
    db_connected = await test_connection()
    if db_connected:
        # 환경변수로 초기화 제어 (기본값: True)
        should_init_db = os.getenv("INIT_DATABASE", "true").lower() == "true"
        if should_init_db:
            # 테이블 생성
            await create_tables()
            logger.info("✅ Railway 데이터베이스 초기화 완료")
        else:
            logger.info("ℹ️ Railway 데이터베이스 초기화가 비활성화되었습니다.")
    else:
        logger.error("❌ Railway 데이터베이스 연결 실패 - 서비스가 시작되지 않습니다")
        raise Exception("Railway PostgreSQL 연결에 실패했습니다")
    
    # Settings 초기화 및 앱 state에 등록
    app.state.settings = Settings()
    
    # 서비스 디스커버리 초기화 및 서비스 등록
    app.state.service_discovery = ServiceDiscovery()
    
    # 기본 서비스 등록
    app.state.service_discovery.register_service(
        service_name="chatbot-service",
        instances=[{"host": "chatbot-service", "port": 8006, "weight": 1}],
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
    return JSONResponse(
        status_code=404,
        content={"detail": "요청한 리소스를 찾을 수 없습니다."}
    )

# 기본 루트 경로
@app.get("/")
async def root():
    return {"message": "Gateway API", "version": "0.1.0"}

# 루트 레벨 헬스 체크
@app.get("/health")
async def health_check_root():
    return {"status": "healthy", "service": "gateway", "path": "root"}

# 데이터베이스 헬스 체크
@app.get("/health/db")
async def health_check_db():
    db_status = await test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "service": "gateway",
        "database": "connected" if db_status else "disconnected"
    }

# 루트 레벨 로그인 페이지 (GET)
@app.get("/login")
async def login_page():
    return {"message": "로그인 페이지", "status": "success"}

# 루트 레벨 회원가입 페이지 (GET)
@app.get("/signup")
async def signup_page():
    return {"message": "회원가입 페이지", "status": "success"}

# 루트 레벨 로그인 처리 (POST)
@app.post("/login")
async def login_process(request: Request):
    logger.info("🔐 로그인 POST 요청 받음")
    try:
        # 요청 본문에서 formData 읽기
        form_data = await request.json()
        logger.info(f"로그인 성공: {form_data}")
        return {"로그인": "성공", "받은 데이터": form_data}
    except Exception as e:
        logger.error(f"로그인 처리 중 오류: {str(e)}")
        return {"로그인": "실패", "오류": str(e)}

# 루트 레벨 회원가입 처리 (POST) - PostgreSQL 저장 기능 포함
@app.post("/signup")
async def signup_process(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("📝 회원가입 POST 요청 받음")
    try:
        # 요청 본문에서 formData 읽기
        form_data = await request.json()
        
        # 필수 필드 검증
        required_fields = ['company_id', 'industry', 'email', 'name', 'age', 'auth_id', 'auth_pw']
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        
        if missing_fields:
            logger.warning(f"필수 필드 누락: {missing_fields}")
            return {
                "회원가입": "실패",
                "message": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
            }
        
        # 새로운 컬럼명에 맞춰 로그 출력
        logger.info("=== 회원가입 요청 데이터 ===")
        logger.info(f"회사 ID: {form_data.get('company_id', 'N/A')}")
        logger.info(f"산업: {form_data.get('industry', 'N/A')}")
        logger.info(f"이메일: {form_data.get('email', 'N/A')}")
        logger.info(f"이름: {form_data.get('name', 'N/A')}")
        logger.info(f"나이: {form_data.get('age', 'N/A')}")
        logger.info(f"인증 ID: {form_data.get('auth_id', 'N/A')}")
        logger.info(f"인증 비밀번호: [PROTECTED]")
        logger.info("==========================")
        
        # PostgreSQL에 사용자 저장
        result = await SignupService.create_user(db, form_data)
        
        if result["success"]:
            logger.info(f"✅ 회원가입 성공: {form_data['email']}")
            return {
                "회원가입": "성공",
                "message": result["message"],
                "user_id": result.get("user_id")
            }
        else:
            logger.warning(f"❌ 회원가입 실패: {result['message']}")
            return {
                "회원가입": "실패",
                "message": result["message"]
            }
            
    except Exception as e:
        logger.error(f"회원가입 처리 중 오류: {str(e)}")
        return {"회원가입": "실패", "오류": str(e)}


# ✅ 서버 실행
if __name__ == "__main__":
    import uvicorn
    # Railway의 PORT 환경변수 사용, 없으면 8080 기본값
    port = int(os.getenv("PORT", os.getenv("SERVICE_PORT", 8080)))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)