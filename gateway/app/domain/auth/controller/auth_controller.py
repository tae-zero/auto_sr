"""
Gateway Auth 컨트롤러
- 인증 관련 API 엔드포인트
- 요청/응답 처리 및 검증
- 동적 라우팅 및 프록시 처리
"""
from fastapi import APIRouter, HTTPException, Depends, Request, UploadFile, File, Query, Form
from typing import Dict, Any, Optional, List
import logging
import httpx
from app.domain.auth.service.auth_service import AuthService
from app.domain.auth.repository.auth_repository import AuthRepository
from app.domain.auth.model.auth_model import AuthRequest, AuthResponse, LoginRequest
from app.domain.auth.schema.auth_schema import AuthValidation
from app.domain.discovery.service_discovery import ServiceDiscovery
from app.common.utility.factory.response_factory import ResponseFactory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["인증"])

# 동적 라우팅을 위한 별도 라우터
dynamic_router = APIRouter(prefix="/api/v1", tags=["Dynamic Routing"])

@router.get("/health")
async def health_check():
    """Gateway Auth 상태 확인"""
    return {
        "status": "healthy",
        "service": "gateway-auth",
        "architecture": "MSV Pattern with Layered Architecture",
        "layers": [
            "Controller Layer - API 엔드포인트",
            "Service Layer - 비즈니스 로직",
            "Repository Layer - 데이터 접근",
            "Entity Layer - 데이터베이스 엔티티",
            "Model Layer - Pydantic 모델",
            "Schema Layer - 데이터 스키마"
        ]
    }

@router.post("/signup", response_model=AuthResponse)
async def signup(request: AuthRequest):
    """회원가입"""
    try:
        logger.info(f"회원가입 요청 받음: {request.dict()}")
        service = AuthService()
        result = await service.process_signup(request)
        return AuthResponse(
            success=True,
            data=result,
            message="회원가입 성공"
        )
    except Exception as e:
        logger.error(f"회원가입 실패: {str(e)}")
        logger.error(f"요청 데이터: {request.dict() if hasattr(request, 'dict') else 'N/A'}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """로그인"""
    try:
        service = AuthService()
        result = await service.process_login(request)
        return AuthResponse(
            success=True,
            data=result,
            message="로그인 성공"
        )
    except Exception as e:
        logger.error(f"로그인 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate", response_model=AuthValidation)
async def validate_token(request: Request):
    """토큰 검증"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다")
        
        service = AuthService()
        result = await service.validate_token(auth_header)
        return AuthValidation(
            valid=True,
            user_info=result,
            message="토큰 검증 성공"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"토큰 검증 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh")
async def refresh_token(request: Request):
    """토큰 갱신"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="인증 토큰이 필요합니다")
        
        service = AuthService()
        result = await service.refresh_token(auth_header)
        return {
            "success": True,
            "data": result,
            "message": "토큰 갱신 성공"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"토큰 갱신 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 동적 라우팅 - main.py에서 이동
@dynamic_router.get("/{service}/{path:path}", summary="GET 프록시")
async def proxy_get(
    service: str, 
    path: str, 
    request: Request
):
    """GET 요청 프록시"""
    try:
        auth_service = AuthService()
        headers = dict(request.headers)
        
        result = await auth_service.forward_request(
            service_name=service,
            path=f"/{path}",
            method="GET",
            headers=headers
        )
        
        return ResponseFactory.create_response(result)
    except Exception as e:
        logger.error(f"Error in GET proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@dynamic_router.post("/{service}/{path:path}", summary="POST 프록시")
async def proxy_post(
    service: str, 
    path: str,
    request: Request,
    file: Optional[UploadFile] = File(None),
    sheet_names: Optional[List[str]] = Query(None, alias="sheet_name")
):
    """POST 요청 프록시"""
    try:
        logger.info(f"🔍 Gateway POST 요청: service={service}, path={path}")
        
        auth_service = AuthService()
        
        # 요청 파라미터 초기화
        files = None
        params = None
        body = None
        
        # 헤더 전달
        headers = dict(request.headers)
        
        # 파일 처리
        if file:
            file_content = await file.read()
            files = {'file': (file.filename, file_content, file.content_type)}
            await file.seek(0)
        
        # 시트 이름 처리
        if sheet_names:
            params = {'sheet_name': sheet_names}
        
        # 본문 처리
        try:
            body = await request.body()
        except Exception:
            body = None
        
        # 서비스에 요청 전달
        result = await auth_service.forward_request(
            service_name=service,
            path=f"/{path}",
            method="POST",
            headers=headers,
            body=body,
            files=files,
            query_params=params
        )
        
        return ResponseFactory.create_response(result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"POST 요청 처리 중 오류 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")

@dynamic_router.put("/{service}/{path:path}", summary="PUT 프록시")
async def proxy_put(service: str, path: str, request: Request):
    """PUT 요청 프록시"""
    try:
        auth_service = AuthService()
        headers = dict(request.headers)
        
        result = await auth_service.forward_request(
            service_name=service,
            path=f"/{path}",
            method="PUT",
            headers=headers,
            body=await request.body()
        )
        return ResponseFactory.create_response(result)
    except Exception as e:
        logger.error(f"Error in PUT proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@dynamic_router.delete("/{service}/{path:path}", summary="DELETE 프록시")
async def proxy_delete(service: str, path: str, request: Request):
    """DELETE 요청 프록시"""
    try:
        auth_service = AuthService()
        headers = dict(request.headers)
        
        result = await auth_service.forward_request(
            service_name=service,
            path=f"/{path}",
            method="DELETE",
            headers=headers,
            body=await request.body()
        )
        return ResponseFactory.create_response(result)
    except Exception as e:
        logger.error(f"Error in DELETE proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@dynamic_router.patch("/{service}/{path:path}", summary="PATCH 프록시")
async def proxy_patch(service: str, path: str, request: Request):
    """PATCH 요청 프록시"""
    try:
        auth_service = AuthService()
        headers = dict(request.headers)
        
        result = await auth_service.forward_request(
            service_name=service,
            path=f"/{path}",
            method="PATCH",
            headers=headers,
            body=await request.body()
        )
        return ResponseFactory.create_response(result)
    except Exception as e:
        logger.error(f"Error in PATCH proxy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

# 동적 라우터를 메인 라우터에 포함
router.include_router(dynamic_router) 