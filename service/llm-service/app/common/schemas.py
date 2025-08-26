from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

# =============================================================================
# 🔍 검색 관련 스키마
# =============================================================================

class SearchRequest(BaseModel):
    """RAG 검색 요청"""
    question: str = Field(..., description="검색할 질문")
    top_k: int = Field(default=5, ge=1, le=20, description="반환할 상위 결과 수")

class SearchHit(BaseModel):
    """검색 결과 히트"""
    rank: int = Field(..., description="순위")
    id: str = Field(..., description="문서 ID")
    score: float = Field(..., description="유사도 점수")
    text: str = Field(..., description="문서 텍스트")
    meta: Dict[str, Any] = Field(..., description="메타데이터")

class SearchResponse(BaseModel):
    """RAG 검색 응답"""
    hits: List[SearchHit] = Field(..., description="검색 결과 히트들")
    context: str = Field(..., description="연결된 컨텍스트")
    service_used: str = Field(..., description="사용된 RAG 서비스")

# =============================================================================
# 📝 초안 생성 관련 스키마
# =============================================================================

class ProviderEnum(str, Enum):
    """생성 모델 프로바이더"""
    OPENAI = "openai"
    KOALPACA = "koalpaca"
    HF = "hf"

class DraftRequest(BaseModel):
    """초안 생성 요청"""
    question: str = Field(..., description="초안 생성 질문")
    sections: List[str] = Field(..., description="생성할 섹션들")
    provider: ProviderEnum = Field(..., description="사용할 생성 모델")
    style_guide: str = Field(default="ESG/회계 전문용어 기준 유지, 수치/근거 인용", description="스타일 가이드")
    top_k: int = Field(default=8, ge=1, le=20, description="검색 컨텍스트 수")

class DraftSection(BaseModel):
    """초안 섹션"""
    section: str = Field(..., description="섹션명")
    content: str = Field(..., description="섹션 내용")

class DraftResponse(BaseModel):
    """초안 생성 응답"""
    draft: str = Field(..., description="생성된 초안 텍스트")
    service_used: str = Field(..., description="사용된 RAG 서비스")

# =============================================================================
# ✨ 윤문 관련 스키마
# =============================================================================

class PolishRequest(BaseModel):
    """윤문 요청"""
    text: str = Field(..., description="윤문할 초안 텍스트")
    tone: str = Field(default="공식적/객관적", description="문체 톤")
    style_guide: str = Field(default="ESG/회계 전문용어 유지, 불필요한 수식어 제거, 한국어 문체 통일", description="스타일 가이드")
    provider: ProviderEnum = Field(..., description="사용할 생성 모델")

class PolishResponse(BaseModel):
    """윤문 응답"""
    polished: str = Field(..., description="정제된 텍스트")
    service_used: str = Field(..., description="사용된 RAG 서비스")

# =============================================================================
# 🔄 원샷 요청 스키마
# =============================================================================

class DraftAndPolishRequest(BaseModel):
    """초안+윤문 원샷 요청"""
    question: str = Field(..., description="초안 생성 질문")
    sections: List[str] = Field(..., description="생성할 섹션들")
    provider: ProviderEnum = Field(..., description="사용할 생성 모델")
    style_guide: str = Field(default="ESG/회계 전문용어 기준 유지, 수치/근거 인용", description="스타일 가이드")
    top_k: int = Field(default=8, ge=1, le=20, description="검색 컨텍스트 수")
    tone: str = Field(default="공식적/객관적", description="윤문 문체 톤")
    polish_style_guide: str = Field(default="ESG/회계 전문용어 유지, 불필요한 수식어 제거, 한국어 문체 통일", description="윤문 스타일 가이드")

class DraftAndPolishResponse(BaseModel):
    """초안+윤문 원샷 응답"""
    draft: str = Field(..., description="생성된 초안 텍스트")
    polished: str = Field(..., description="정제된 텍스트")
    service_used: str = Field(..., description="사용된 RAG 서비스")

# =============================================================================
# 📁 FAISS 업로드 관련 스키마
# =============================================================================

class UploadResponse(BaseModel):
    """FAISS 파일 업로드 응답"""
    ok: bool = Field(..., description="업로드 성공 여부")
    size: Dict[str, int] = Field(..., description="업로드된 파일 크기 (바이트)")
    load_results: Dict[str, bool] = Field(..., description="RAG 서비스별 인덱스 로딩 결과")

# =============================================================================
# 💚 헬스체크 관련 스키마
# =============================================================================

class HealthResponse(BaseModel):
    """헬스체크 응답"""
    ok: bool = Field(..., description="서비스 상태")
    service_name: str = Field(..., description="서비스명")
    version: str = Field(..., description="서비스 버전")
    rag_services: Dict[str, Dict[str, Any]] = Field(..., description="RAG 서비스별 상태")
    all_services_loaded: bool = Field(..., description="모든 RAG 서비스 로딩 상태")
    embed_dim: int = Field(..., description="임베딩 차원")
    timestamp: float = Field(..., description="응답 타임스탬프")
    error: Optional[str] = Field(None, description="에러 메시지")

# =============================================================================
# ⚠️ 에러 관련 스키마
# =============================================================================

class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")
    request_id: Optional[str] = Field(None, description="요청 ID")
