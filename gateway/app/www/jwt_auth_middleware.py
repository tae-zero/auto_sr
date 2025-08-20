from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # 인증 제외할 엔드포인트들
            if request.url.path in ["/health", "/login", "/api/v1/signup", "/", "/docs", "/openapi.json", "/redoc"] or request.url.path.startswith("/api/v1/tcfd/") or request.url.path.startswith("/api/v1/tcfdreport/"):
                return await self.app(scope, receive, send)
            
            # JWT 토큰 검증 (간단한 구현)
            try:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    # 여기에 실제 JWT 검증 로직 추가
                    # 현재는 토큰이 있으면 통과
                    user_id = self.extract_user_id_from_token(token)
                    if user_id:
                        # 사용자 ID를 헤더에 추가
                        scope["headers"] = list(scope["headers"]) + [
                            (b"x-user-id", str(user_id).encode())
                        ]
                else:
                    # 토큰이 없어도 통과 (개발 환경)
                    logger.warning("No Authorization header found")
                    
            except Exception as e:
                logger.error(f"Auth middleware error: {str(e)}")
                # 개발 환경에서는 인증 오류를 무시
                pass
                
        return await self.app(scope, receive, send)
    
    def extract_user_id_from_token(self, token: str) -> Optional[str]:
        """토큰에서 사용자 ID 추출 (간단한 구현)"""
        try:
            # 실제로는 JWT 디코딩 로직이 들어가야 함
            # 현재는 토큰이 있으면 "user123" 반환
            return "user123" if token else None
        except Exception as e:
            logger.error(f"Token extraction error: {str(e)}")
            return None 