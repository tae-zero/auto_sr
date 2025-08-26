import logging
from typing import Dict, Optional, List, Tuple
from .base_rag_service import BaseRAGService
from .openai_rag_service import OpenAIRAGService
from .huggingface_rag_service import HuggingFaceRAGService
from ...common.schemas import SearchHit

logger = logging.getLogger(__name__)

class RAGManager:
    """2개 RAG 시스템을 관리하는 매니저"""
    
    def __init__(self):
        self.services: Dict[str, BaseRAGService] = {}
        self.default_service = "openai"
        
        # OpenAI RAG 서비스 초기화
        try:
            self.services["openai"] = OpenAIRAGService()
            logger.info("OpenAI RAG 서비스 초기화 완료")
        except Exception as e:
            logger.error(f"OpenAI RAG 서비스 초기화 실패: {e}")
        
        # Hugging Face RAG 서비스 초기화
        try:
            self.services["huggingface"] = HuggingFaceRAGService()
            logger.info("Hugging Face RAG 서비스 초기화 완료")
        except Exception as e:
            logger.error(f"Hugging Face RAG 서비스 초기화 실패: {e}")
        
        logger.info(f"RAG 매니저 초기화 완료: {list(self.services.keys())} 서비스")
    
    def get_service(self, service_name: str = None) -> BaseRAGService:
        """지정된 RAG 서비스를 반환합니다."""
        if service_name is None:
            service_name = self.default_service
        
        if service_name not in self.services:
            raise ValueError(f"지원하지 않는 RAG 서비스: {service_name}")
        
        return self.services[service_name]
    
    def load_all_indices(self) -> Dict[str, bool]:
        """모든 RAG 서비스의 인덱스를 로드합니다."""
        results = {}
        
        for service_name, service in self.services.items():
            try:
                success = service.load_index()
                results[service_name] = success
                logger.info(f"{service_name} 인덱스 로딩: {'성공' if success else '실패'}")
            except Exception as e:
                logger.error(f"{service_name} 인덱스 로딩 실패: {e}")
                results[service_name] = False
        
        return results
    
    def search(self, query: str, top_k: int = 5, service_name: str = None) -> Tuple[List[SearchHit], str]:
        """지정된 RAG 서비스로 검색을 수행합니다."""
        service = self.get_service(service_name)
        return service.search(query, top_k)
    
    def generate_draft(self, question: str, sections: List[str], top_k: int = 8, service_name: str = None) -> str:
        """지정된 RAG 서비스로 초안을 생성합니다."""
        service = self.get_service(service_name)
        return service.generate_draft(question, sections, top_k)
    
    def polish_text(self, text: str, tone: str = "공식적", style_guide: str = "", service_name: str = None) -> str:
        """지정된 RAG 서비스로 텍스트를 윤문합니다."""
        service = self.get_service(service_name)
        return service.polish_text(text, tone, style_guide)
    
    def get_service_status(self) -> Dict[str, Dict]:
        """모든 서비스의 상태를 반환합니다."""
        status = {}
        
        for service_name, service in self.services.items():
            status[service_name] = {
                "name": service.service_name,
                "is_loaded": service.is_loaded,
                "type": service.get_service_info()["type"]
            }
        
        return status
    
    def get_available_services(self) -> List[str]:
        """사용 가능한 서비스 목록을 반환합니다."""
        return list(self.services.keys())
    
    def is_service_available(self, service_name: str) -> bool:
        """지정된 서비스가 사용 가능한지 확인합니다."""
        return service_name in self.services and self.services[service_name].is_loaded
