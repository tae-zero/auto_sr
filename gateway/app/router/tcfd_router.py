from fastapi import APIRouter, Request, HTTPException, Header, Depends
from app.domain.discovery.service_discovery import ServiceDiscovery
from app.router.auth_router import verify_token
import httpx
import logging
import traceback
import os
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tcfd", tags=["tcfd"])

@router.get("/standards")
async def get_tcfd_standards(request: Request, authorization: str = Header(None)):
    """TCFD 표준 정보 전체 조회"""
    try:
        logger.info("🔍 TCFD 표준 정보 조회 요청 시작")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Auth Service 응답 구조에 맞게 사용자 정보 추출
        user_data = user_info.get('user_info', {})
        if not user_data:
            logger.warning("⚠️ 사용자 정보가 없습니다")
            user_data = {}
        
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        # 등록된 모든 TCFD Service 인스턴스 확인
        all_tcfd_instances = service_discovery.get_service_instances("tcfd-service")
        logger.info(f"🔍 등록된 모든 TCFD Service 인스턴스: {all_tcfd_instances}")
        
        tcfd_service = service_discovery.get_service_instance("tcfd-service")
        logger.info(f"🎯 선택된 TCFD Service 인스턴스: {tcfd_service}")
        
        if not tcfd_service:
            logger.error("❌ TCFD Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service.host
        port = tcfd_service.port
        logger.info(f"🔍 원본 TCFD Service host: {host}")
        logger.info(f"🔍 TCFD Service port: {port}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        logger.info(f"🔍 USE_RAILWAY_TCFD: {os.getenv('USE_RAILWAY_TCFD')}")
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            # Docker 환경에서는 http:// 사용, Railway에서는 https:// 사용
            if os.getenv("RAILWAY_ENVIRONMENT") in ["true", "production"]:
                host = f"https://{host}"
                logger.info(f"🔧 Railway 환경: https:// 추가됨")
            else:
                host = f"http://{host}"
                logger.info(f"🔧 Docker 환경: http:// 추가됨")
        
        logger.info(f"🌐 TCFD Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/standards")
        
        # 사용자 정보를 쿼리 파라미터로 전달
        user_params = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "company_id": user_data.get("company_id")
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # HTTPS URL에는 포트를 추가하지 않음 (Railway는 기본 443 포트 사용)
            if host.startswith("https://"):
                url = f"{host}/api/v1/tcfd/standards"
            else:
                # HTTP URL에만 포트 추가 (Docker 환경)
                url = f"{host}:{port}/api/v1/tcfd/standards" if port else f"{host}/api/v1/tcfd/standards"
            
            logger.info(f"📤 최종 요청 URL: {url}")
            logger.info(f"📤 사용자 정보: {user_params}")
            logger.info(f"📤 Authorization 헤더: {authorization}")
            
            # Authorization 헤더와 사용자 정보를 함께 전달
            headers = {"Authorization": authorization}
            response = await client.get(url, params=user_params, headers=headers)
            logger.info(f"📥 TCFD Service 응답 상태: {response.status_code}")
            logger.info(f"📥 TCFD Service 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Service 응답 데이터: {response_data}")
            return response_data
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Service 요청 실패: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"TCFD Service 요청 실패: {str(e)}")

@router.get("/company-overview")
async def get_company_overview(request: Request, company_name: str, authorization: str = Header(None)):
    """회사별 기업개요 정보 조회"""
    try:
        logger.info(f"🔍 회사별 기업개요 정보 조회 요청 시작: {company_name}")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Auth Service 응답 구조에 맞게 사용자 정보 추출
        user_data = user_info.get('user_info', {})
        if not user_data:
            logger.warning("⚠️ 사용자 정보가 없습니다")
            user_data = {}
        
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        # 등록된 모든 TCFD Service 인스턴스 확인
        all_tcfd_instances = service_discovery.get_service_instances("tcfd-service")
        logger.info(f"🔍 등록된 모든 TCFD Service 인스턴스: {all_tcfd_instances}")
        
        tcfd_service = service_discovery.get_service_instance("tcfd-service")
        logger.info(f"🎯 선택된 TCFD Service 인스턴스: {tcfd_service}")
        
        if not tcfd_service:
            logger.error("❌ TCFD Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service.host
        port = tcfd_service.port
        logger.info(f"🔍 원본 TCFD Service host: {host}")
        logger.info(f"🔍 TCFD Service port: {port}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        logger.info(f"🔍 USE_RAILWAY_TCFD: {os.getenv('USE_RAILWAY_TCFD')}")
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            # Docker 환경에서는 http:// 사용, Railway에서는 https:// 사용
            if os.getenv("RAILWAY_ENVIRONMENT") in ["true", "production"]:
                host = f"https://{host}"
                logger.info(f"🔧 Railway 환경: https:// 추가됨")
            else:
                host = f"http://{host}"
                logger.info(f"🔧 Docker 환경: http:// 추가됨")
        
        logger.info(f"🌐 TCFD Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/company-overview")
        
        # 사용자 정보를 쿼리 파라미터로 전달
        user_params = {
            "company_name": company_name,
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "company_id": user_data.get("company_id")
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # HTTPS URL에는 포트를 추가하지 않음 (Railway는 기본 443 포트 사용)
            if host.startswith("https://"):
                url = f"{host}/api/v1/tcfd/company-overview"
            else:
                # HTTP URL에만 포트 추가 (Docker 환경)
                url = f"{host}:{port}/api/v1/tcfd/company-overview" if port else f"{host}/api/v1/tcfd/company-overview"
            
            logger.info(f"📤 최종 요청 URL: {url}")
            logger.info(f"📤 사용자 정보: {user_params}")
            logger.info(f"📤 Authorization 헤더: {authorization}")
            
            # Authorization 헤더와 사용자 정보를 함께 전달
            headers = {"Authorization": authorization}
            response = await client.get(url, params=user_params, headers=headers)
            logger.info(f"📥 TCFD Service 응답 상태: {response.status_code}")
            logger.info(f"📥 TCFD Service 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Service 응답 데이터: {response_data}")
            return response_data
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Service 요청 실패: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"TCFD Service 요청 실패: {str(e)}")

@router.get("/standards/{category}")
async def get_tcfd_standards_by_category(request: Request, category: str, authorization: str = Header(None)):
    """카테고리별 TCFD 표준 정보 조회"""
    try:
        logger.info(f"🔍 카테고리별 TCFD 표준 정보 조회 요청 시작: {category}")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Auth Service 응답 구조에 맞게 사용자 정보 추출
        user_data = user_info.get('user_info', {})
        if not user_data:
            logger.warning("⚠️ 사용자 정보가 없습니다")
            user_data = {}
        
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        # 등록된 모든 TCFD Service 인스턴스 확인
        all_tcfd_instances = service_discovery.get_service_instances("tcfd-service")
        logger.info(f"🔍 등록된 모든 TCFD Service 인스턴스: {all_tcfd_instances}")
        
        tcfd_service = service_discovery.get_service_instance("tcfd-service")
        logger.info(f"🎯 선택된 TCFD Service 인스턴스: {tcfd_service}")
        
        if not tcfd_service:
            logger.error("❌ TCFD Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service.host
        port = tcfd_service.port
        logger.info(f"🔍 원본 TCFD Service host: {host}")
        logger.info(f"🔍 TCFD Service port: {port}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        logger.info(f"🔍 USE_RAILWAY_TCFD: {os.getenv('USE_RAILWAY_TCFD')}")
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            # Docker 환경에서는 http:// 사용, Railway에서는 https:// 사용
            if os.getenv("RAILWAY_ENVIRONMENT") in ["true", "production"]:
                host = f"https://{host}"
                logger.info(f"🔧 Railway 환경: https:// 추가됨")
            else:
                host = f"http://{host}"
                logger.info(f"🔧 Docker 환경: http:// 추가됨")
        
        logger.info(f"🌐 TCFD Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/standards/{category}")
        
        # 사용자 정보를 쿼리 파라미터로 전달
        user_params = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "company_id": user_data.get("company_id")
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # HTTPS URL에는 포트를 추가하지 않음 (Railway는 기본 443 포트 사용)
            if host.startswith("https://"):
                url = f"{host}/api/v1/tcfd/standards/{category}"
            else:
                # HTTP URL에만 포트 추가 (Docker 환경)
                url = f"{host}:{port}/api/v1/tcfd/standards/{category}" if port else f"{host}/api/v1/tcfd/standards/{category}"
            
            logger.info(f"📤 최종 요청 URL: {url}")
            logger.info(f"📤 사용자 정보: {user_params}")
            logger.info(f"📤 Authorization 헤더: {authorization}")
            
            # Authorization 헤더와 사용자 정보를 함께 전달
            headers = {"Authorization": authorization}
            response = await client.get(url, params=user_params, headers=headers)
            logger.info(f"📥 TCFD Service 응답 상태: {response.status_code}")
            logger.info(f"📥 TCFD Service 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Service 응답 데이터: {response_data}")
            return response_data
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Service 요청 실패: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"TCFD Service 요청 실패: {str(e)}")

@router.get("/companies")
async def get_companies(request: Request, authorization: str = Header(None)):
    """회사 목록 조회"""
    try:
        logger.info("🔍 회사 목록 조회 요청 시작")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Auth Service 응답 구조에 맞게 사용자 정보 추출
        user_data = user_info.get('user_info', {})
        if not user_data:
            logger.warning("⚠️ 사용자 정보가 없습니다")
            user_data = {}
        
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        # 등록된 모든 TCFD Service 인스턴스 확인
        all_tcfd_instances = service_discovery.get_service_instances("tcfd-service")
        logger.info(f"🔍 등록된 모든 TCFD Service 인스턴스: {all_tcfd_instances}")
        
        tcfd_service = service_discovery.get_service_instance("tcfd-service")
        logger.info(f"🎯 선택된 TCFD Service 인스턴스: {tcfd_service}")
        
        if not tcfd_service:
            logger.error("❌ TCFD Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service.host
        port = tcfd_service.port
        logger.info(f"🔍 원본 TCFD Service host: {host}")
        logger.info(f"🔍 TCFD Service port: {port}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        logger.info(f"🔍 USE_RAILWAY_TCFD: {os.getenv('USE_RAILWAY_TCFD')}")
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            # Docker 환경에서는 http:// 사용, Railway에서는 https:// 사용
            if os.getenv("RAILWAY_ENVIRONMENT") in ["true", "production"]:
                host = f"https://{host}"
                logger.info(f"🔧 Railway 환경: https:// 추가됨")
            else:
                host = f"http://{host}"
                logger.info(f"🔧 Docker 환경: http:// 추가됨")
        
        logger.info(f"🌐 TCFD Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/companies")
        
        # 사용자 정보를 쿼리 파라미터로 전달
        user_params = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "company_id": user_data.get("company_id")
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # HTTPS URL에는 포트를 추가하지 않음 (Railway는 기본 443 포트 사용)
            if host.startswith("https://"):
                url = f"{host}/api/v1/tcfd/companies"
            else:
                # HTTP URL에만 포트 추가 (Docker 환경)
                url = f"{host}:{port}/api/v1/tcfd/companies" if port else f"{host}/api/v1/tcfd/companies"
            
            logger.info(f"📤 최종 요청 URL: {url}")
            logger.info(f"📤 사용자 정보: {user_params}")
            logger.info(f"📤 Authorization 헤더: {authorization}")
            
            # Authorization 헤더와 사용자 정보를 함께 전달
            headers = {"Authorization": authorization}
            response = await client.get(url, params=user_params, headers=headers)
            logger.info(f"📥 TCFD Service 응답 상태: {response.status_code}")
            logger.info(f"📥 TCFD Service 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Service 응답 데이터: {response_data}")
            return response_data
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Service 요청 실패: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"TCFD Service 요청 실패: {str(e)}")

@router.get("/company-financial-data")
async def get_company_financial_data(request: Request, company_name: str, authorization: str = Header(None)):
    """회사별 재무정보 조회"""
    try:
        logger.info(f"🔍 회사별 재무정보 조회 요청 시작: {company_name}")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Auth Service 응답 구조에 맞게 사용자 정보 추출
        user_data = user_info.get('user_info', {})
        if not user_data:
            logger.warning("⚠️ 사용자 정보가 없습니다")
            user_data = {}
        
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        # 등록된 모든 TCFD Service 인스턴스 확인
        all_tcfd_instances = service_discovery.get_service_instances("tcfd-service")
        logger.info(f"🔍 등록된 모든 TCFD Service 인스턴스: {all_tcfd_instances}")
        
        tcfd_service = service_discovery.get_service_instance("tcfd-service")
        logger.info(f"🎯 선택된 TCFD Service 인스턴스: {tcfd_service}")
        
        if not tcfd_service:
            logger.error("❌ TCFD Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service.host
        port = tcfd_service.port
        logger.info(f"🔍 원본 TCFD Service host: {host}")
        logger.info(f"🔍 TCFD Service port: {port}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        logger.info(f"🔍 USE_RAILWAY_TCFD: {os.getenv('USE_RAILWAY_TCFD')}")
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            # Docker 환경에서는 http:// 사용, Railway에서는 https:// 사용
            if os.getenv("RAILWAY_ENVIRONMENT") in ["true", "production"]:
                host = f"https://{host}"
                logger.info(f"🔧 Railway 환경: https:// 추가됨")
            else:
                host = f"http://{host}"
                logger.info(f"🔧 Docker 환경: http:// 추가됨")
        
        logger.info(f"🌐 TCFD Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/company-financial-data")
        logger.info(f"📤 요청 파라미터: company_name={company_name}")
        
        # 사용자 정보를 쿼리 파라미터로 전달
        user_params = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "company_id": user_data.get("company_id")
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # 포트가 있는 경우에만 포트 추가
            if host.startswith("https://"):
                url = f"{host}/api/v1/tcfd/company-financial-data"
            else:
                url = f"{host}:{port}/api/v1/tcfd/company-financial-data" if port else f"{host}/api/v1/tcfd/company-financial-data"
            
            logger.info(f"📤 최종 요청 URL: {url}")
            logger.info(f"📤 사용자 정보: {user_params}")
            logger.info(f"📤 Authorization 헤더: {authorization}")
            
            # Authorization 헤더와 사용자 정보를 함께 전달
            headers = {"Authorization": authorization}
            response = await client.get(
                url,
                params={"company_name": company_name, **user_params},
                headers=headers
            )
            logger.info(f"📥 TCFD Service 응답 상태: {response.status_code}")
            logger.info(f"📥 TCFD Service 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Service 응답 데이터: {response_data}")
            return response_data
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Service 요청 실패: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"TCFD Service 요청 실패: {str(e)}")



@router.get("/inputs")
async def get_tcfd_inputs(request: Request, authorization: str = Header(None)):
    """TCFD 입력 데이터 조회 (가장 최신 데이터 포함)"""
    try:
        logger.info("🔍 TCFD 입력 데이터 조회 요청 시작")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Auth Service 응답 구조에 맞게 사용자 정보 추출
        user_data = user_info.get('user_info', {})
        if not user_data:
            logger.warning("⚠️ 사용자 정보가 없습니다")
            user_data = {}
        
        # Service Discovery를 통해 TCFD Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        tcfd_service = service_discovery.get_service_instance("tcfd-service")
        logger.info(f"🎯 선택된 TCFD Service 인스턴스: {tcfd_service}")
        
        if not tcfd_service:
            logger.error("❌ TCFD Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="TCFD Service를 찾을 수 없습니다")
        
        # TCFD Service로 요청 전달
        host = tcfd_service.host
        port = tcfd_service.port
        logger.info(f"🔍 원본 TCFD Service host: {host}")
        logger.info(f"🔍 TCFD Service port: {port}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            # Docker 환경에서는 http:// 사용, Railway에서는 https:// 사용
            if os.getenv("RAILWAY_ENVIRONMENT") in ["true", "production"]:
                host = f"https://{host}"
                logger.info(f"🔧 Railway 환경: https:// 추가됨")
            else:
                host = f"http://{host}"
                logger.info(f"🔧 Docker 환경: http:// 추가됨")
        
        logger.info(f"🌐 TCFD Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/api/v1/tcfd/inputs")
        
        # 사용자 정보를 쿼리 파라미터로 전달
        user_params = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "company_id": user_data.get("company_id")
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Docker 환경에서는 컨테이너 이름과 포트 사용, Railway에서는 환경변수 사용
            if os.getenv("RAILWAY_ENVIRONMENT") in ["true", "production"]:
                # Railway 환경에서는 환경변수에서 직접 TCFD Service URL 가져오기
                railway_tcfd_url = os.getenv("RAILWAY_TCFD_SERVICE_URL")
                if railway_tcfd_url:
                    url = f"{railway_tcfd_url}/api/v1/tcfd/inputs"
                    logger.info(f"🔧 Railway 환경에서 TCFD Service URL: {url}")
                else:
                    # 환경변수가 없으면 Service Discovery에서 가져온 URL 사용
                    url = f"{host}/api/v1/tcfd/inputs"
                    logger.info(f"🔧 Railway 환경에서 Service Discovery TCFD Service URL: {url}")
            else:
                # Docker 환경에서는 컨테이너 이름과 포트 사용
                url = f"http://tcfd-service:8005/api/v1/tcfd/inputs"
                logger.info(f"🔧 Docker 환경에서 TCFD Service URL: {url}")
            
            logger.info(f"📤 최종 요청 URL: {url}")
            logger.info(f"📤 사용자 정보: {user_params}")
            logger.info(f"📤 Authorization 헤더: {authorization}")
            
            # Authorization 헤더와 사용자 정보를 함께 전달
            headers = {"Authorization": authorization}
            response = await client.get(
                url,
                params=user_params,
                headers=headers
            )
            logger.info(f"📥 TCFD Service 응답 상태: {response.status_code}")
            logger.info(f"📥 TCFD Service 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ TCFD Service 응답 데이터: {response_data}")
            return response_data
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ TCFD Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"TCFD Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ TCFD Service 요청 실패: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"TCFD Service 요청 실패: {str(e)}")

@router.post("/generate-report")
async def generate_tcfd_report(request: Request, authorization: str = Header(None)):
    """TCFD 보고서 생성 (LLM Service로 요청 전달)"""
    try:
        logger.info("🔍 TCFD 보고서 생성 요청 시작")
        
        # JWT 토큰 검증
        if not authorization or not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Bearer 토큰이 필요합니다")
        
        # 토큰 검증 및 사용자 정보 추출
        user_info = await verify_token(authorization)
        logger.info(f"✅ 토큰 검증 성공, 사용자: {user_info.get('user_info', {}).get('user_id', 'unknown')}")
        
        # Auth Service 응답 구조에 맞게 사용자 정보 추출
        user_data = user_info.get('user_info', {})
        if not user_data:
            logger.warning("⚠️ 사용자 정보가 없습니다")
            user_data = {}
        
        # Service Discovery를 통해 LLM Service 인스턴스 가져오기
        service_discovery: ServiceDiscovery = request.app.state.service_discovery
        logger.info(f"📡 Service Discovery 상태: {service_discovery}")
        
        llm_service = service_discovery.get_service_instance("llm-service")
        logger.info(f"🎯 선택된 LLM Service 인스턴스: {llm_service}")
        
        if not llm_service:
            logger.error("❌ LLM Service를 찾을 수 없습니다")
            raise HTTPException(status_code=503, detail="LLM Service를 찾을 수 없습니다")
        
        # LLM Service로 요청 전달
        host = llm_service.host
        port = llm_service.port
        logger.info(f"🔍 원본 LLM Service host: {host}")
        logger.info(f"🔍 LLM Service port: {port}")
        logger.info(f"🔍 RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT')}")
        
        # URL이 이미 완전한 형태인지 확인
        if not host.startswith(('http://', 'https://')):
            # Docker 환경에서는 http:// 사용, Railway에서는 https:// 사용
            if os.getenv("RAILWAY_ENVIRONMENT") in ["true", "production"]:
                host = f"https://{host}"
                logger.info(f"🔧 Railway 환경: https:// 추가됨")
            else:
                host = f"http://{host}"
                logger.info(f"🔧 Docker 환경: http:// 추가됨")
        
        logger.info(f"🌐 LLM Service URL: {host}")
        logger.info(f"📤 요청 엔드포인트: {host}/tcfd/generate-report")
        
        # 사용자 정보를 쿼리 파라미터로 전달
        user_params = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "company_id": user_data.get("company_id")
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Railway 환경에서는 실제 서비스 URL 사용, Docker에서는 컨테이너 이름 사용
            railway_llm_url = os.getenv("RAILWAY_LLM_SERVICE_URL")
            if railway_llm_url:
                url = f"{railway_llm_url}/tcfd/generate-report"
                logger.info(f"🔧 Railway/Vercel 환경에서 환경변수 LLM Service URL: {url}")
            else:
                # Docker 환경에서는 컨테이너 이름과 포트 사용
                url = f"http://llm-service:8002/tcfd/generate-report"
                logger.info(f"🔧 Docker 환경에서 LLM Service URL: {url}")
            
            logger.info(f"📤 최종 요청 URL: {url}")
            logger.info(f"📤 사용자 정보: {user_params}")
            logger.info(f"📤 Authorization 헤더: {authorization}")
            
            # 요청 본문 읽기
            request_body = await request.json()
            logger.info(f"📤 요청 본문: {request_body}")
            
            # Authorization 헤더와 사용자 정보를 함께 전달
            headers = {"Authorization": authorization}
            response = await client.post(
                url,
                json=request_body,
                headers=headers
            )
            logger.info(f"📥 LLM Service 응답 상태: {response.status_code}")
            logger.info(f"📥 LLM Service 응답 헤더: {dict(response.headers)}")
            
            response.raise_for_status()
            response_data = response.json()
            logger.info(f"✅ LLM Service 응답 데이터: {response_data}")
            return response_data
            
    except HTTPException:
        raise
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ LLM Service HTTP 응답 오류: {e.response.status_code}")
        logger.error(f"❌ 응답 내용: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"LLM Service 응답 오류: {e.response.status_code}")
    except Exception as e:
        logger.error(f"❌ LLM Service 요청 실패: {str(e)}")
        logger.error(f"❌ 오류 타입: {type(e).__name__}")
        logger.error(f"❌ 스택 트레이스: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"LLM Service 요청 실패: {str(e)}")

