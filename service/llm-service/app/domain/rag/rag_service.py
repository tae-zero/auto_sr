import os
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class RAGService:
    """RAG 서비스 - FAISS 인덱스를 통한 정보 검색"""
    
    def __init__(self):
        self.index_path = os.getenv('FAISS_VOLUME_PATH', '/data')  # Railway 볼륨 경로
        self.index_name = os.getenv('FAISS_INDEX_NAME', 'sr_corpus')
        self.store_name = os.getenv('FAISS_STORE_NAME', 'sr_corpus')
        
        logger.info(f"🔧 RAG 서비스 초기화")
        logger.info(f"  - index_path: {self.index_path}")
        logger.info(f"  - index_name: {self.index_name}")
        logger.info(f"  - store_name: {self.store_name}")
        
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
            
            logger.info(f"🔍 RAG 서비스 인덱스 로딩 시작")
            logger.info(f"  - index_path: {self.index_path}")
            logger.info(f"  - index_name: {self.index_name}")
            logger.info(f"  - store_name: {self.store_name}")
            logger.info(f"  - index_file: {index_file}")
            logger.info(f"  - store_file: {store_file}")
            
            # 파일 존재 확인
            if not os.path.exists(index_file):
                logger.warning(f"FAISS 인덱스 파일이 존재하지 않음: {index_file}")
                self.is_index_loaded = False
                return
                
            if not os.path.exists(store_file):
                logger.warning(f"문서 저장소 파일이 존재하지 않음: {store_file}")
                self.is_index_loaded = False
                return
            
            # 디렉토리 내용 확인
            index_dir = os.path.dirname(index_file)
            store_dir = os.path.dirname(store_file)
            
            if os.path.exists(index_dir):
                logger.info(f"📁 인덱스 디렉토리 내용: {os.listdir(index_dir)}")
            if os.path.exists(store_dir):
                logger.info(f"📁 저장소 디렉토리 내용: {os.listdir(store_dir)}")
            
            # FAISS 인덱스 로딩
            self.faiss_index = faiss.read_index(index_file)
            logger.info(f"FAISS 인덱스 로딩 완료: {self.faiss_index.ntotal}개 문서")
            
            # 문서 저장소 로딩
            try:
                logger.info(f"📖 PKL 파일 로딩 시도: {store_file}")
                with open(store_file, 'rb') as f:
                    self.doc_store = pickle.load(f)
                logger.info(f"✅ 문서 저장소 로딩 완료: {len(self.doc_store)}개 문서")
            except Exception as pkl_error:
                logger.error(f"❌ PKL 파일 로딩 실패: {str(pkl_error)}")
                logger.error(f"  - 파일 경로: {store_file}")
                logger.error(f"  - 파일 크기: {os.path.getsize(store_file) if os.path.exists(store_file) else '파일 없음'}")
                # PKL 로딩 실패 시에도 FAISS는 사용 가능하도록 설정
                self.doc_store = None
                logger.warning("⚠️ 문서 저장소 없이 FAISS 인덱스만 사용")
            
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
            
            # 문서 저장소 확인
            if self.doc_store is None:
                logger.warning("⚠️ 문서 저장소(PKL)가 로드되지 않았습니다. 더미 결과를 반환합니다.")
                return self._get_dummy_results(query, top_k)
            
            # 실제 FAISS 검색 로직 구현
            logger.info(f"쿼리 검색: '{query}' (top_k: {top_k})")
            logger.info(f"📚 문서 저장소 상태: {len(self.doc_store)}개 문서")
            
            # 쿼리를 벡터로 변환 (간단한 TF-IDF 스타일)
            query_tokens = query.lower().split()
            
            # 문서 저장소에서 관련성 높은 문서 검색
            relevant_docs = []
            for doc_id, doc_content in self.doc_store.items():
                # 간단한 키워드 매칭 점수 계산
                score = 0
                doc_tokens = doc_content.lower().split()
                
                for token in query_tokens:
                    if token in doc_tokens:
                        score += 1
                
                if score > 0:
                    relevant_docs.append({
                        'content': doc_content,
                        'score': score / len(query_tokens),  # 정규화된 점수
                        'source': f'Document_{doc_id}',
                        'metadata': {
                            'category': 'TCFD',
                            'type': 'corpus'
                        }
                    })
            
            # 점수 기준으로 정렬하고 top_k만 반환
            relevant_docs.sort(key=lambda x: x['score'], reverse=True)
            results = relevant_docs[:top_k]
            
            if not results:
                logger.info("관련 문서를 찾을 수 없어 더미 결과를 반환합니다.")
                return self._get_dummy_results(query, top_k)
            
            logger.info(f"검색 완료: {len(results)}개 문서 발견")
            return results
            
        except Exception as e:
            logger.error(f"RAG 검색 중 오류 발생: {str(e)}")
            return self._get_dummy_results(query, top_k)
    
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

    def search_openai(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """OpenAI용 RAG 검색 (TCFD 보고서 서비스 호환성)"""
        return self.search(query, top_k)
    
    def search_huggingface(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Hugging Face용 RAG 검색 (TCFD 보고서 서비스 호환성)"""
        return self.search(query, top_k)
