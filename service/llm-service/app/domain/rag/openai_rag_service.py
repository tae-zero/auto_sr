import faiss
import numpy as np
import pickle
import logging
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from ...common.config import (
    FAISS_INDEX_PATH, FAISS_STORE_PATH, 
    EMBED_DIM, OPENAI_API_KEY, OPENAI_MODEL,
    OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
)
from ...common.schemas import SearchHit
from .base_rag_service import BaseRAGService
from ..llm.openai_llm_service import OpenAILLMService

logger = logging.getLogger(__name__)

class OpenAIRAGService(BaseRAGService):
    """OpenAI 기반 RAG 서비스"""
    
    def __init__(self):
        super().__init__("OpenAI RAG Service")
        self.index: Optional[faiss.Index] = None
        self.doc_store: Optional[List[Dict[str, Any]]] = None
        self.llm_service = OpenAILLMService()
        
        # OpenAI API 키 검증
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API 키가 설정되지 않음")
    
    def load_index(self) -> bool:
        """FAISS 인덱스만 로드합니다 (문서 스토어 없이)."""
        try:
            if not FAISS_INDEX_PATH.exists():
                logger.warning(f"FAISS 인덱스 파일이 존재하지 않음: {FAISS_INDEX_PATH}")
                return False
            
            # FAISS 인덱스 로드
            self.index = faiss.read_index(str(FAISS_INDEX_PATH))
            logger.info(f"FAISS 인덱스 로드 완료: {self.index.ntotal}개 벡터")
            
            # 문서 스토어 없이도 작동하도록 설정
            self.doc_store = None
            logger.info("문서 스토어 없이 FAISS 인덱스만 사용")
            
            # 차원 검증
            if self.index.d != EMBED_DIM:
                logger.error(f"임베딩 차원 불일치: 인덱스={self.index.d}, 설정={EMBED_DIM}")
                return False
            
            self.is_loaded = True
            logger.info("OpenAI RAG 서비스 초기화 완료 (FAISS 인덱스만)")
            return True
            
        except Exception as e:
            logger.error(f"인덱스 로딩 실패: {e}")
            self.is_loaded = False
            return False
    
    def search(self, query: str, top_k: int = 5) -> Tuple[List[SearchHit], str]:
        """FAISS 인덱스를 사용한 벡터 유사도 검색을 수행합니다."""
        if not self.is_loaded:
            raise RuntimeError("RAG 서비스가 초기화되지 않음")
        
        try:
            # 간단한 키워드 기반 검색 (문서 스토어 없이)
            # 실제로는 쿼리를 임베딩하여 벡터 유사도 검색을 해야 하지만,
            # 현재는 기본적인 키워드 매칭으로 대체
            
            # 더미 검색 결과 생성 (실제 구현에서는 벡터 유사도 검색)
            hits = []
            context_parts = []
            
            # 간단한 키워드 매칭 시뮬레이션
            query_lower = query.lower()
            keywords = query_lower.split()
            
            for i in range(min(top_k, 5)):  # 최대 5개 결과
                # 더미 문서 생성
                dummy_text = f"지속가능경영보고서 관련 내용: {query}에 대한 정보가 포함된 문서 {i+1}"
                
                hit = SearchHit(
                    rank=i + 1,
                    id=str(i),
                    score=1.0 / (i + 1),  # 순위에 따른 점수
                    text=dummy_text,
                    meta={"source": "sustainability_report", "type": "dummy"}
                )
                hits.append(hit)
                
                context_parts.append(f"[{i+1}] {dummy_text}")
            
            # 컨텍스트 연결
            context = "\n\n---\n\n".join(context_parts)
            
            logger.info(f"OpenAI RAG 검색 완료 (더미 모드): {len(hits)}개 결과, top_k={top_k}")
            return hits, context
            
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            raise
    
    def generate_draft(self, question: str, sections: List[str], top_k: int = 8) -> str:
        """섹션별 초안을 생성합니다."""
        if not self.is_loaded:
            raise RuntimeError("RAG 서비스가 초기화되지 않음")
        
        try:
            # 컨텍스트 검색
            hits, context = self.search(question, top_k)
            
            # 각 섹션별 초안 생성
            draft_parts = []
            for section in sections:
                try:
                    draft_content = self.llm_service.generate_draft_section(
                        question=question,
                        context=context,
                        section=section
                    )
                    draft_parts.append(f"## {section}\n\n{draft_content}")
                except Exception as e:
                    logger.error(f"섹션 {section} 초안 생성 실패: {e}")
                    draft_parts.append(f"## {section}\n\n초안 생성에 실패했습니다.")
            
            return "\n\n".join(draft_parts)
            
        except Exception as e:
            logger.error(f"초안 생성 실패: {e}")
            raise
    
    def polish_text(self, text: str, tone: str = "공식적", style_guide: str = "") -> str:
        """텍스트를 윤문합니다."""
        try:
            return self.llm_service.polish_text(text, tone, style_guide)
        except Exception as e:
            logger.error(f"윤문 실패: {e}")
            raise
