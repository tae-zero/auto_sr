import faiss
import numpy as np
import pickle
import logging
import requests
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from ...common.config import (
    get_faiss_index_path, get_faiss_store_path,
    EMBED_DIM, HF_API_TOKEN, HF_MODEL, HF_API_URL
)
from ...common.schemas import SearchHit
from .base_rag_service import BaseRAGService
from ..llm.huggingface_llm_service import HuggingFaceLLMService

logger = logging.getLogger(__name__)

class HuggingFaceRAGService(BaseRAGService):
    """Hugging Face 기반 RAG 서비스 (코알파, RoLA 학습용)"""
    
    def __init__(self):
        super().__init__("Hugging Face RAG Service")
        self.index: Optional[faiss.Index] = None
        self.doc_store: Optional[List[Dict[str, Any]]] = None
        self.llm_service = HuggingFaceLLMService()
        
        # Hugging Face API 설정 검증
        if not HF_API_TOKEN:
            logger.warning("Hugging Face API 토큰이 설정되지 않음")
        if not HF_API_URL:
            logger.warning("Hugging Face API URL이 설정되지 않음")
    
    def load_index(self) -> bool:
        """FAISS 인덱스와 문서 저장소를 로드합니다."""
        try:
            if not get_faiss_index_path().exists():
                logger.warning(f"FAISS 인덱스 파일이 존재하지 않음: {get_faiss_index_path()}")
                return False
            
            # FAISS 인덱스 로드
            self.index = faiss.read_index(str(get_faiss_index_path()))
            logger.info(f"FAISS 인덱스 로드 완료: {self.index.ntotal}개 벡터")
            
            # 문서 저장소 로딩 시도
            try:
                store_path = get_faiss_store_path()
                logger.info(f"📖 PKL 문서 저장소 로딩 시도: {store_path}")
                
                if store_path.exists():
                    with open(store_path, 'rb') as f:
                        self.doc_store = pickle.load(f)
                    logger.info(f"✅ 문서 저장소 로딩 완료: {len(self.doc_store)}개 문서")
                else:
                    logger.warning(f"⚠️ 문서 저장소 파일이 존재하지 않음: {store_path}")
                    self.doc_store = None
            except Exception as pkl_error:
                logger.error(f"❌ PKL 파일 로딩 실패: {str(pkl_error)}")
                
                # Pydantic 호환성 문제 시도 해결
                if '__fields_set__' in str(pkl_error):
                    logger.info("🔄 Pydantic v1/v2 호환성 문제 감지, 대체 방법 시도")
                    try:
                        # pickle5 또는 다른 로더 시도
                        import pickle5
                        with open(store_path, 'rb') as f:
                            self.doc_store = pickle5.load(f)
                        logger.info(f"✅ pickle5로 문서 저장소 로딩 성공: {len(self.doc_store)}개 문서")
                    except ImportError:
                        logger.info("pickle5가 설치되지 않음, Pydantic v2 호환성 처리 시도")
                        try:
                            # Pydantic v1 객체를 v2로 변환하는 시도
                            with open(store_path, 'rb') as f:
                                raw_data = pickle.load(f)
                            
                            # v1 객체의 __fields_set__ 문제 해결
                            if isinstance(raw_data, dict):
                                # 딕셔너리 형태로 변환 시도
                                converted_data = {}
                                for key, value in raw_data.items():
                                    if hasattr(value, '__dict__'):
                                        # 객체를 딕셔너리로 변환
                                        converted_data[key] = value.__dict__
                                    else:
                                        converted_data[key] = value
                                self.doc_store = converted_data
                                logger.info(f"✅ Pydantic v1/v2 호환성 처리로 문서 저장소 로딩 성공: {len(self.doc_store)}개 문서")
                            else:
                                raise Exception("데이터 형태 변환 실패")
                                
                        except Exception as compat_error:
                            logger.error(f"❌ Pydantic 호환성 해결 시도 실패: {str(compat_error)}")
                            self.doc_store = None
                            logger.warning("⚠️ 문서 저장소 없이 FAISS 인덱스만 사용")
                    except Exception as pkl5_error:
                        logger.error(f"❌ pickle5 로딩도 실패: {str(pkl5_error)}")
                        self.doc_store = None
                        logger.warning("⚠️ 문서 저장소 없이 FAISS 인덱스만 사용")
                else:
                    self.doc_store = None
                    logger.warning("⚠️ 문서 저장소 없이 FAISS 인덱스만 사용")
            
            # 차원 검증
            if self.index.d != EMBED_DIM:
                logger.error(f"임베딩 차원 불일치: 인덱스={self.index.d}, 설정={EMBED_DIM}")
                return False
            
            self.is_loaded = True
            if self.doc_store:
                logger.info("Hugging Face RAG 서비스 초기화 완료 (FAISS 인덱스 + 문서 저장소)")
            else:
                logger.info("Hugging Face RAG 서비스 초기화 완료 (FAISS 인덱스만)")
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
            
            logger.info(f"Hugging Face RAG 검색 완료: {len(hits)}개 결과, top_k={top_k}")
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
