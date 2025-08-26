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
        """FAISS 인덱스와 문서 스토어를 로드합니다."""
        try:
            if not FAISS_INDEX_PATH.exists():
                logger.warning(f"FAISS 인덱스 파일이 존재하지 않음: {FAISS_INDEX_PATH}")
                return False
            
            if not FAISS_STORE_PATH.exists():
                logger.warning(f"문서 스토어 파일이 존재하지 않음: {FAISS_STORE_PATH}")
                return False
            
            # FAISS 인덱스 로드
            self.index = faiss.read_index(str(FAISS_INDEX_PATH))
            logger.info(f"FAISS 인덱스 로드 완료: {self.index.ntotal}개 벡터")
            
            # 문서 스토어 로드
            with open(FAISS_STORE_PATH, 'rb') as f:
                self.doc_store = pickle.load(f)
            logger.info(f"문서 스토어 로드 완료: {len(self.doc_store)}개 문서")
            
            # 차원 검증
            if self.index.d != EMBED_DIM:
                logger.error(f"임베딩 차원 불일치: 인덱스={self.index.d}, 설정={EMBED_DIM}")
                return False
            
            self.is_loaded = True
            logger.info("OpenAI RAG 서비스 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"인덱스 로딩 실패: {e}")
            self.is_loaded = False
            return False
    
    def search(self, query: str, top_k: int = 5) -> Tuple[List[SearchHit], str]:
        """키워드 기반 검색을 수행합니다."""
        if not self.is_loaded:
            raise RuntimeError("RAG 서비스가 초기화되지 않음")
        
        try:
            hits = []
            context_parts = []
            
            # 키워드 매칭 검색
            query_lower = query.lower()
            
            for idx, doc in enumerate(self.doc_store):
                text = doc.get('text', '').lower()
                if query_lower in text:
                    # 간단한 점수 계산
                    score = 1.0 / (1.0 + len(text.split()))
                    
                    hit = SearchHit(
                        rank=len(hits) + 1,
                        id=str(idx),
                        score=score,
                        text=doc.get('text', ''),
                        meta=doc.get('meta', {})
                    )
                    hits.append(hit)
                    
                    # 컨텍스트 구성
                    context_part = f"[{len(hits)}] {doc.get('text', '')}"
                    if doc.get('meta', {}).get('source'):
                        context_part += f" (출처: {doc['meta']['source']})"
                    context_parts.append(context_part)
                    
                    if len(hits) >= top_k:
                        break
            
            # 점수 순으로 정렬
            hits.sort(key=lambda x: x.score, reverse=True)
            
            # 컨텍스트 연결
            context = "\n\n---\n\n".join(context_parts)
            
            logger.info(f"OpenAI RAG 검색 완료: {len(hits)}개 결과, top_k={top_k}")
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
