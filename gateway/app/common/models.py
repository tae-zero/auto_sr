from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class GatewayStatus(BaseModel):
    """Gateway 상태 응답 모델"""
    message: str = Field(description="Gateway 상태 메시지")
    services: List[str] = Field(description="등록된 서비스 목록")
    timestamp: float = Field(description="응답 시간 (Unix timestamp)")
    version: str = Field(description="Gateway 버전")

class HealthStatus(BaseModel):
    """헬스 체크 응답 모델"""
    status: str = Field(description="헬스 상태 (healthy/unhealthy)")
    gateway: str = Field(description="Gateway 상태")

class ServiceInstanceInfo(BaseModel):
    """서비스 인스턴스 정보 모델"""
    host: str = Field(description="인스턴스 호스트")
    port: int = Field(description="인스턴스 포트")
    weight: int = Field(description="로드 밸런싱 가중치")
    health: bool = Field(description="헬스 상태")
    last_health_check: str = Field(description="마지막 헬스 체크 시간")
    connection_count: int = Field(description="현재 연결 수")
    response_time: float = Field(description="응답 시간 (초)")
    metadata: Dict[str, Any] = Field(description="메타데이터", default_factory=dict)

class ServiceStatus(BaseModel):
    """서비스 상태 모델"""
    service_name: str = Field(description="서비스명")
    total_instances: int = Field(description="전체 인스턴스 수")
    healthy_instances: int = Field(description="헬시한 인스턴스 수")
    load_balancer_type: str = Field(description="로드 밸런서 타입")
    instances: List[ServiceInstanceInfo] = Field(description="인스턴스 목록")

class ServiceHealthCheck(BaseModel):
    """서비스 헬스 체크 응답 모델"""
    service: str = Field(description="서비스명")
    status: str = Field(description="헬스 상태 (healthy/unhealthy)")
    response_time: Optional[float] = Field(description="응답 시간 (초)")
    instance: Optional[str] = Field(description="선택된 인스턴스")
    error: Optional[str] = Field(description="에러 메시지 (헬스 체크 실패 시)")

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    detail: str = Field(description="에러 상세 메시지")
    error_code: Optional[str] = Field(description="에러 코드")
    timestamp: datetime = Field(description="에러 발생 시간")

class UserResponse(BaseModel):
    """사용자 응답 모델"""
    message: str = Field(description="응답 메시지")

class ProxyResponse(BaseModel):
    """프록시 응답 모델"""
    content: Any = Field(description="프록시된 서비스의 응답 내용")
    status_code: int = Field(description="HTTP 상태 코드")
    headers: Dict[str, str] = Field(description="응답 헤더")
    service: str = Field(description="대상 서비스명")
    target_url: str = Field(description="대상 URL")
    response_time: float = Field(description="응답 시간 (초)")
    instance: str = Field(description="선택된 인스턴스") 