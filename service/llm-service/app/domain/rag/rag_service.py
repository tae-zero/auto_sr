import os
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class RAGService:
    """RAG 서비스 - FAISS 인덱스를 통한 정보 검색"""
    
    def __init__(self):
        self.index_path = os.getenv('FAISS_VOLUME_PATH', '/app/vectordb')
        self.index_name = os.getenv('FAISS_INDEX_NAME', 'sr_corpus')
        self.store_name = os.getenv('FAISS_STORE_NAME', 'sr_corpus')
        
        # FAISS 인덱스 로딩 상태
        self.is_index_loaded = False
        self.faiss_index = None
        self.doc_store = None
        
        # 인덱스 로딩 시도
        self._load_index()
    
    def _load_index(self):
        """FAISS 인덱스와 문서 저장소 로딩"""
        try:
            import faiss
            import pickle
            
            # FAISS 인덱스 파일 경로
            index_file = os.path.join(self.index_path, self.index_name, "index.faiss")
            store_file = os.path.join(self.index_path, self.store_name, "index.pkl")
            
            # 파일 존재 확인
            if not os.path.exists(index_file):
                logger.warning(f"FAISS 인덱스 파일이 존재하지 않음: {index_file}")
                self.is_index_loaded = False
                return
                
            if not os.path.exists(store_file):
                logger.warning(f"문서 저장소 파일이 존재하지 않음: {store_file}")
                self.is_index_loaded = False
                return
            
            # FAISS 인덱스 로딩
            self.faiss_index = faiss.read_index(index_file)
            logger.info(f"FAISS 인덱스 로딩 완료: {self.faiss_index.ntotal}개 문서")
            
            # 문서 저장소 로딩
            with open(store_file, 'rb') as f:
                self.doc_store = pickle.load(f)
            logger.info(f"문서 저장소 로딩 완료: {len(self.doc_store)}개 문서")
            
            self.is_index_loaded = True
            logger.info("FAISS 인덱스 로딩 완료")
            
        except Exception as e:
            logger.error(f"FAISS 인덱스 로딩 실패: {str(e)}")
            self.is_index_loaded = False
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """쿼리를 기반으로 관련 문서 검색"""
        try:
            if not self.is_index_loaded:
                logger.warning("FAISS 인덱스가 로딩되지 않았습니다. 더미 결과를 반환합니다.")
                return self._get_dummy_results(query, top_k)
            
            # 실제 FAISS 검색 로직 구현
            # 임시로 더미 결과 반환 (나중에 실제 검색 로직으로 교체)
            logger.info(f"쿼리 검색: '{query}' (top_k: {top_k})")
            return self._get_dummy_results(query, top_k)
            
        except Exception as e:
            logger.error(f"RAG 검색 중 오류 발생: {str(e)}")
            return []
    
    def _get_dummy_results(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """더미 검색 결과 반환 (테스트용)"""
        dummy_results = []
        
        # TCFD 관련 더미 데이터
        tcfd_content = [
            "TCFD(Task Force on Climate-related Financial Disclosures)는 기후 관련 재무정보 공시를 위한 국제 표준 프레임워크입니다.",
            "거버넌스 영역에서는 기후 관련 위험과 기회에 대한 이사회 감독 및 경영진 역할을 명확히 해야 합니다.",
            "전략 영역에서는 기후 관련 위험과 기회가 비즈니스 모델에 미치는 영향을 분석하고 시나리오 분석을 수행해야 합니다.",
            "위험관리 영역에서는 기후 관련 위험을 식별, 평가, 관리하는 프로세스를 전사적 위험관리 체계에 통합해야 합니다.",
            "지표 및 목표 영역에서는 기후 관련 위험과 기회를 평가하는 지표를 설정하고 구체적인 목표를 수립해야 합니다."
        ]
        
        for i in range(min(top_k, len(tcfd_content))):
            dummy_results.append({
                'content': tcfd_content[i],
                'score': 0.9 - (i * 0.1),
                'source': f'TCFD_Standard_{i+1}',
                'metadata': {
                    'category': 'TCFD',
                    'type': 'standard'
                }
            })
        
        return dummy_results
    
    def get_service_status(self) -> Dict[str, Any]:
        """RAG 서비스 상태 반환"""
        return {
            'is_loaded': self.is_index_loaded,
            'index_path': self.index_path,
            'index_name': self.index_name,
            'store_name': self.store_name
        }
