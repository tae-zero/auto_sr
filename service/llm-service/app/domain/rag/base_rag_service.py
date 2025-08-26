from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional
import logging
from ...common.schemas import SearchHit

logger = logging.getLogger(__name__)

class BaseRAGService(ABC):
    """RAG 서비스의 기본 추상 클래스"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.is_loaded = False
        logger.info(f"{service_name} RAG 서비스 초기화")
    
    @abstractmethod
    def load_index(self) -> bool:
        """FAISS 인덱스와 문서 스토어를 로드합니다."""
        pass
    
    @abstractmethod
    def search(self, query: str, top_k: int = 5) -> Tuple[List[SearchHit], str]:
        """쿼리로 검색을 수행합니다."""
        pass
    
    @abstractmethod
    def generate_draft(self, question: str, sections: List[str], top_k: int = 8) -> str:
        """초안을 생성합니다."""
        pass
    
    @abstractmethod
    def polish_text(self, text: str, tone: str = "공식적", style_guide: str = "") -> str:
        """텍스트를 윤문합니다."""
        pass
    
    def get_context_for_sections(self, question: str, top_k: int = 8) -> Tuple[List[SearchHit], str]:
        """섹션별 초안 생성을 위한 컨텍스트를 가져옵니다."""
        return self.search(question, top_k)
    
    def format_context_with_metadata(self, hits: List[SearchHit]) -> str:
        """메타데이터를 포함하여 컨텍스트를 포맷팅합니다."""
        context_parts = []
        
        for i, hit in enumerate(hits):
            # 메타데이터 정보 추가
            meta_info = []
            if hit.meta.get('source'):
                meta_info.append(f"출처: {hit.meta['source']}")
            if hit.meta.get('year'):
                meta_info.append(f"연도: {hit.meta['year']}")
            if hit.meta.get('section'):
                meta_info.append(f"섹션: {hit.meta['section']}")
            if hit.meta.get('page'):
                meta_info.append(f"페이지: {hit.meta['page']}")
            
            meta_str = f" ({', '.join(meta_info)})" if meta_info else ""
            
            context_part = f"[{i+1}] {hit.text}{meta_str}"
            context_parts.append(context_part)
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_service_info(self) -> Dict[str, Any]:
        """서비스 정보를 반환합니다."""
        return {
            "service_name": self.service_name,
            "is_loaded": self.is_loaded,
            "type": "rag_service"
        }
