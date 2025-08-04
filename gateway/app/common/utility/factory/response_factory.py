from fastapi.responses import JSONResponse
from typing import Any, Dict

class ResponseFactory:
    """응답 생성 팩토리 클래스"""
    
    @staticmethod
    def create_response(response: Any) -> Any:
        """응답 객체 생성"""
        if hasattr(response, 'status_code'):
            # HTTP 응답 객체인 경우
            return response
        elif isinstance(response, dict):
            # 딕셔너리인 경우 JSON 응답으로 변환
            return JSONResponse(content=response)
        else:
            # 기타 타입은 그대로 반환
            return response
    
    @staticmethod
    def create_error_response(message: str, status_code: int = 500) -> JSONResponse:
        """에러 응답 생성"""
        return JSONResponse(
            content={"detail": message},
            status_code=status_code
        )
    
    @staticmethod
    def create_success_response(data: Any, message: str = "Success") -> JSONResponse:
        """성공 응답 생성"""
        return JSONResponse(
            content={
                "message": message,
                "data": data
            }
        ) 