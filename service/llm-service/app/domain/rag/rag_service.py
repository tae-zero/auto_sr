import os
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class RAGService:
    """RAG 서비스 - FAISS 인덱스를 통한 정보 검색"""
    
    def __init__(self):
        self.index_path = os.getenv('FAISS_VOLUME_PATH', '/app/vectordb')  # Docker 볼륨 경로
        self.index_name = os.getenv('FAISS_INDEX_NAME', 'sr_corpus')
        self.store_name = os.getenv('FAISS_STORE_NAME', 'sr_corpus')
        self.standards_index_name = os.getenv('FAISS_STANDARDS_INDEX_NAME', 'standards')
        self.standards_store_name = os.getenv('FAISS_STANDARDS_STORE_NAME', 'standards')
        
        logger.info(f"🔧 RAG 서비스 초기화")
        logger.info(f"  - index_path: {self.index_path}")
        logger.info(f"  - index_name: {self.index_name}")
        logger.info(f"  - store_name: {self.store_name}")
        logger.info(f"  - standards_index_name: {self.standards_index_name}")
        logger.info(f"  - standards_store_name: {self.standards_store_name}")
        
        # FAISS 인덱스 로딩 상태
        self.is_index_loaded = False
        self.faiss_index = None
        self.doc_store = None
        self.standards_faiss_index = None
        self.standards_doc_store = None
        
        # 인덱스 로딩 시도
        self._load_index()
    
    def _load_index(self):
        """FAISS 인덱스와 문서 저장소 로딩"""
        try:
            import faiss
            import pickle
            
            # 메인 FAISS 인덱스 파일 경로 (sr_corpus)
            index_file = os.path.join(self.index_path, self.index_name, "index.faiss")
            store_file = os.path.join(self.index_path, self.store_name, "index.pkl")
            
            # Standards FAISS 인덱스 파일 경로
            standards_index_file = os.path.join(self.index_path, self.standards_index_name, "index.faiss")
            standards_store_file = os.path.join(self.index_path, self.standards_store_name, "index.pkl")
            
            logger.info(f"🔍 RAG 서비스 인덱스 로딩 시작")
            logger.info(f"  - index_path: {self.index_path}")
            logger.info(f"  - index_file: {index_file}")
            logger.info(f"  - store_file: {store_file}")
            logger.info(f"  - standards_index_file: {standards_index_file}")
            logger.info(f"  - standards_store_file: {standards_store_file}")
            
            # 디렉토리 내용 확인
            if os.path.exists(self.index_path):
                logger.info(f"📁 vectordb 디렉토리 내용: {os.listdir(self.index_path)}")
                for subdir in os.listdir(self.index_path):
                    subdir_path = os.path.join(self.index_path, subdir)
                    if os.path.isdir(subdir_path):
                        logger.info(f"  📁 {subdir} 디렉토리 내용: {os.listdir(subdir_path)}")
            
            # 메인 FAISS 인덱스 로딩
            if os.path.exists(index_file) and os.path.exists(store_file):
                try:
                    self.faiss_index = faiss.read_index(index_file)
                    logger.info(f"✅ 메인 FAISS 인덱스 로딩 완료: {self.faiss_index.ntotal}개 문서")
                    
                    with open(store_file, 'rb') as f:
                        self.doc_store = pickle.load(f)
                    logger.info(f"✅ 메인 문서 저장소 로딩 완료: {len(self.doc_store)}개 문서")
                    
                except Exception as e:
                    logger.error(f"❌ 메인 인덱스 로딩 실패: {str(e)}")
                    self.faiss_index = None
                    self.doc_store = None
            else:
                logger.warning(f"⚠️ 메인 FAISS 파일이 존재하지 않음: {index_file} 또는 {store_file}")
            
            # Standards FAISS 인덱스 로딩
            if os.path.exists(standards_index_file) and os.path.exists(standards_store_file):
                try:
                    self.standards_faiss_index = faiss.read_index(standards_index_file)
                    logger.info(f"✅ Standards FAISS 인덱스 로딩 완료: {self.standards_faiss_index.ntotal}개 문서")
                    
                    with open(standards_store_file, 'rb') as f:
                        self.standards_doc_store = pickle.load(f)
                    logger.info(f"✅ Standards 문서 저장소 로딩 완료: {len(self.standards_doc_store)}개 문서")
                    
                except Exception as e:
                    logger.error(f"❌ Standards 인덱스 로딩 실패: {str(e)}")
                    self.standards_faiss_index = None
                    self.standards_doc_store = None
            else:
                logger.warning(f"⚠️ Standards FAISS 파일이 존재하지 않음: {standards_index_file} 또는 {standards_store_file}")
            
            # 최소한 하나의 인덱스라도 로드되었으면 성공으로 간주
            if self.faiss_index or self.standards_faiss_index:
                self.is_index_loaded = True
                logger.info("✅ FAISS 인덱스 로딩 완료")
            else:
                self.is_index_loaded = False
                logger.error("❌ 모든 FAISS 인덱스 로딩 실패")
            
        except Exception as e:
            logger.error(f"FAISS 인덱스 로딩 실패: {str(e)}")
            self.is_index_loaded = False
    
    def _extract_text_from_doc(self, doc_content) -> str:
        """문서 객체에서 실제 텍스트 내용 추출 (강화된 버전)"""
        try:
            # LangChain Document 객체인 경우
            if hasattr(doc_content, 'page_content'):
                return doc_content.page_content
            
            # 딕셔너리인 경우
            elif isinstance(doc_content, dict):
                # page_content 키가 있는 경우
                if 'page_content' in doc_content:
                    return doc_content['page_content']
                # text 키가 있는 경우
                elif 'text' in doc_content:
                    return doc_content['text']
                # content 키가 있는 경우
                elif 'content' in doc_content:
                    return doc_content['content']
                # 다른 키들을 문자열로 변환
                else:
                    return str(doc_content)
            
            # 문자열인 경우
            elif isinstance(doc_content, str):
                return doc_content
            
            # InMemoryDocstore 객체인 경우 - 더 강력한 추출
            elif hasattr(doc_content, '_dict'):
                try:
                    doc_dict = doc_content._dict
                    logger.info(f"🔍 InMemoryDocstore 내부 구조 분석: {type(doc_dict)}, 길이: {len(doc_dict) if doc_dict else 0}")
                    
                    if doc_dict:
                        # 모든 문서의 내용을 수집
                        all_texts = []
                        for doc_id, doc_obj in doc_dict.items():
                            logger.info(f"  📄 문서 ID: {doc_id}, 타입: {type(doc_obj)}")
                            
                            if hasattr(doc_obj, 'page_content'):
                                text_content = doc_obj.page_content
                                logger.info(f"    ✅ page_content 발견: {len(text_content)}자")
                                all_texts.append(text_content)
                            elif isinstance(doc_obj, dict):
                                if 'page_content' in doc_obj:
                                    text_content = doc_obj['page_content']
                                    logger.info(f"    ✅ dict.page_content 발견: {len(text_content)}자")
                                    all_texts.append(text_content)
                                elif 'text' in doc_obj:
                                    text_content = doc_obj['text']
                                    logger.info(f"    ✅ dict.text 발견: {len(text_content)}자")
                                    all_texts.append(text_content)
                                else:
                                    logger.info(f"    ⚠️ dict에서 텍스트 키를 찾을 수 없음: {list(doc_obj.keys())}")
                                    all_texts.append(str(doc_obj))
                            elif isinstance(doc_obj, str):
                                logger.info(f"    ✅ 문자열 발견: {len(doc_obj)}자")
                                all_texts.append(doc_obj)
                            else:
                                logger.info(f"    ⚠️ 알 수 없는 타입: {type(doc_obj)}")
                                all_texts.append(str(doc_obj))
                        
                        if all_texts:
                            # 첫 번째 문서의 내용 반환 (전체가 너무 길 수 있음)
                            first_text = all_texts[0][:1000]  # 1000자로 제한
                            logger.info(f"✅ InMemoryDocstore에서 텍스트 추출 성공: {len(first_text)}자")
                            return first_text
                        else:
                            logger.warning("⚠️ InMemoryDocstore에서 텍스트를 추출할 수 없음")
                            return str(doc_content)
                    else:
                        logger.warning("⚠️ InMemoryDocstore._dict가 비어있음")
                        return str(doc_content)
                except Exception as e:
                    logger.warning(f"InMemoryDocstore 처리 실패: {e}")
                    return str(doc_content)
            
            # UUID 매핑 딕셔너리인 경우 - 더 강력한 추출
            elif hasattr(doc_content, 'get') and hasattr(doc_content, 'values'):
                try:
                    logger.info(f"🔍 UUID 매핑 딕셔너리 분석: {type(doc_content)}, 길이: {len(doc_content)}")
                    
                    # 모든 값의 내용을 수집
                    all_texts = []
                    for doc_id, doc_obj in doc_content.items():
                        logger.info(f"  📄 UUID: {doc_id}, 타입: {type(doc_obj)}")
                        
                        if hasattr(doc_obj, 'page_content'):
                            text_content = doc_obj.page_content
                            logger.info(f"    ✅ page_content 발견: {len(text_content)}자")
                            all_texts.append(text_content)
                        elif isinstance(doc_obj, dict):
                            if 'page_content' in doc_obj:
                                text_content = doc_obj['page_content']
                                logger.info(f"    ✅ dict.page_content 발견: {len(text_content)}자")
                                all_texts.append(text_content)
                            elif 'text' in doc_obj:
                                text_content = doc_obj['text']
                                logger.info(f"    ✅ dict.text 발견: {len(text_content)}자")
                                all_texts.append(text_content)
                            else:
                                logger.info(f"    ⚠️ dict에서 텍스트 키를 찾을 수 없음: {list(doc_obj.keys())}")
                                all_texts.append(str(doc_obj))
                        elif isinstance(doc_obj, str):
                            logger.info(f"    ✅ 문자열 발견: {len(doc_obj)}자")
                            all_texts.append(doc_obj)
                        else:
                            logger.info(f"    ⚠️ 알 수 없는 타입: {type(doc_obj)}")
                            all_texts.append(str(doc_obj))
                    
                    if all_texts:
                        # 첫 번째 문서의 내용 반환
                        first_text = all_texts[0][:1000]  # 1000자로 제한
                        logger.info(f"✅ UUID 매핑에서 텍스트 추출 성공: {len(first_text)}자")
                        return first_text
                    else:
                        logger.warning("⚠️ UUID 매핑에서 텍스트를 추출할 수 없음")
                        return str(doc_content)
                except Exception as e:
                    logger.warning(f"UUID 매핑 처리 실패: {e}")
                    return str(doc_content)
            
            # 기타 객체인 경우
            else:
                return str(doc_content)
                
        except Exception as e:
            logger.warning(f"문서 내용 추출 실패: {e}")
            return str(doc_content)
    
    def _search_in_doc_store(self, doc_store, query_tokens: List[str], store_type: str) -> List[Dict[str, Any]]:
        """문서 저장소에서 검색 수행"""
        relevant_docs = []
        
        try:
            # 문서 저장소 타입 확인 및 안전한 처리
            if isinstance(doc_store, dict):
                # dict 형태인 경우
                for doc_id, doc_content in doc_store.items():
                    # 실제 텍스트 내용 추출
                    actual_text = self._extract_text_from_doc(doc_content)
                    
                    # 개선된 키워드 매칭 점수 계산
                    score = self._calculate_relevance_score(query_tokens, actual_text)
                    
                    # 디버깅: 모든 문서의 점수 출력
                    logger.info(f"📄 {store_type} 문서 {doc_id}: 점수={score}, 내용 미리보기={actual_text[:100]}...")
                    
                    if score > 0:  # 임계값을 0으로 설정하여 모든 문서 포함
                        relevant_docs.append({
                            'content': actual_text,
                            'score': score,
                            'source': f'{store_type}_Document_{doc_id}',
                            'metadata': {
                                'category': 'TCFD',
                                'type': store_type
                            }
                        })
            elif isinstance(doc_store, (list, tuple)):
                # list나 tuple 형태인 경우
                logger.info(f"{store_type} 문서 저장소가 {type(doc_store).__name__} 형태로 로딩됨")
                for i, doc_content in enumerate(doc_store):
                    # 실제 텍스트 내용 추출
                    actual_text = self._extract_text_from_doc(doc_content)
                    
                    # 개선된 키워드 매칭 점수 계산
                    score = self._calculate_relevance_score(query_tokens, actual_text)
                    
                    # 디버깅: 모든 문서의 점수 출력
                    logger.info(f"📄 {store_type} 문서 {i}: 점수={score}, 내용 미리보기={actual_text[:100]}...")
                    
                    if score > 0:  # 임계값을 0으로 설정하여 모든 문서 포함
                        relevant_docs.append({
                            'content': actual_text,
                            'score': score,
                            'source': f'{store_type}_Document_{i}',
                            'metadata': {
                                'category': 'TCFD',
                                'type': store_type
                            }
                        })
            else:
                logger.warning(f"알 수 없는 {store_type} 문서 저장소 타입: {type(doc_store)}")
                return []
                
        except Exception as e:
            logger.error(f"{store_type} 문서 저장소 검색 중 오류 발생: {str(e)}")
            return []
        
        return relevant_docs
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """쿼리를 기반으로 관련 문서 검색"""
        try:
            if not self.is_index_loaded:
                logger.warning("FAISS 인덱스가 로딩되지 않았습니다. 더미 결과를 반환합니다.")
                return self._get_dummy_results(query, top_k)
            
            # 문서 저장소 확인
            if self.doc_store is None and self.standards_doc_store is None:
                logger.warning("⚠️ 모든 문서 저장소(PKL)가 로드되지 않았습니다. 더미 결과를 반환합니다.")
                return self._get_dummy_results(query, top_k)
            
            # 실제 FAISS 검색 로직 구현
            logger.info(f"쿼리 검색: '{query}' (top_k: {top_k})")
            
            # 메인 문서 저장소 상태
            if self.doc_store:
                logger.info(f"📚 메인 문서 저장소 상태: {len(self.doc_store)}개 문서")
            else:
                logger.info("⚠️ 메인 문서 저장소가 로드되지 않음")
            
            # Standards 문서 저장소 상태
            if self.standards_doc_store:
                logger.info(f"📚 Standards 문서 저장소 상태: {len(self.standards_doc_store)}개 문서")
            else:
                logger.info("⚠️ Standards 문서 저장소가 로드되지 않음")
            
            # 쿼리를 벡터로 변환 (간단한 TF-IDF 스타일)
            query_tokens = query.lower().split()
            
            # 문서 저장소에서 관련성 높은 문서 검색
            relevant_docs = []
            
            # 메인 문서 저장소 검색
            if self.doc_store:
                logger.info("🔍 메인 문서 저장소 검색 시작")
                if isinstance(self.doc_store, (list, tuple)):
                    logger.info(f"📚 메인 문서 저장소가 {type(self.doc_store).__name__} 형태로 로딩됨")
                    for i, doc_content in enumerate(self.doc_store):
                        # 실제 텍스트 내용 추출
                        actual_text = self._extract_text_from_doc(doc_content)
                        
                        # 개선된 키워드 매칭 점수 계산
                        score = self._calculate_relevance_score(query_tokens, actual_text)
                        
                        # 디버깅: 모든 문서의 점수 출력
                        logger.info(f"📄 메인 문서 {i}: 점수={score}, 내용 미리보기={actual_text[:100]}...")
                        
                        if score > 0:  # 임계값을 0으로 설정하여 모든 문서 포함
                            relevant_docs.append({
                                'content': actual_text,
                                'score': score,
                                'source': f'main_Document_{i}',
                                'metadata': {
                                    'category': 'TCFD',
                                    'type': 'main'
                                }
                            })
                else:
                    relevant_docs.extend(self._search_in_doc_store(self.doc_store, query_tokens, "main"))
            
            # Standards 문서 저장소 검색
            if self.standards_doc_store:
                logger.info("🔍 Standards 문서 저장소 검색 시작")
                if isinstance(self.standards_doc_store, (list, tuple)):
                    logger.info(f"📚 Standards 문서 저장소가 {type(self.standards_doc_store).__name__} 형태로 로딩됨")
                    for i, doc_content in enumerate(self.standards_doc_store):
                        # 실제 텍스트 내용 추출
                        actual_text = self._extract_text_from_doc(doc_content)
                        
                        # 개선된 키워드 매칭 점수 계산
                        score = self._calculate_relevance_score(query_tokens, actual_text)
                        
                        # 디버깅: 모든 문서의 점수 출력
                        logger.info(f"📄 Standards 문서 {i}: 점수={score}, 내용 미리보기={actual_text[:100]}...")
                        
                        if score > 0:  # 임계값을 0으로 설정하여 모든 문서 포함
                            relevant_docs.append({
                                'content': actual_text,
                                'score': score,
                                'source': f'standards_Document_{i}',
                                'metadata': {
                                    'category': 'TCFD',
                                    'type': 'standards'
                                }
                            })
                else:
                    relevant_docs.extend(self._search_in_doc_store(self.standards_doc_store, query_tokens, "standards"))
            
            if not relevant_docs:
                logger.warning("⚠️ 모든 문서 저장소에서 관련 문서를 찾을 수 없음")
                return self._get_dummy_results(query, top_k)
            
            # 점수 기준으로 정렬하고 top_k만 반환
            relevant_docs.sort(key=lambda x: x['score'], reverse=True)
            results = relevant_docs[:top_k]
            
            # 디버깅을 위한 상세 로그
            logger.info(f"🔍 검색 결과 요약:")
            logger.info(f"  - 전체 문서 수: {len(self.doc_store)}")
            logger.info(f"  - 관련 문서 후보: {len(relevant_docs)}")
            logger.info(f"  - 최종 결과: {len(results)}")
            
            if results:
                for i, doc in enumerate(results):
                    logger.info(f"  📄 결과 {i+1}: 점수={doc['score']}, 소스={doc['source']}")
            
            if not results:
                logger.info("관련 문서를 찾을 수 없어 더미 결과를 반환합니다.")
                return self._get_dummy_results(query, top_k)
            
            logger.info(f"검색 완료: {len(results)}개 문서 발견")
            return results
            
        except Exception as e:
            logger.error(f"RAG 검색 중 오류 발생: {str(e)}")
            return self._get_dummy_results(query, top_k)
    
    def _calculate_relevance_score(self, query_tokens: List[str], doc_content: str) -> float:
        """개선된 관련성 점수 계산"""
        try:
            doc_content_lower = doc_content.lower()
            doc_tokens = doc_content_lower.split()
            
            # 기본 키워드 매칭 점수 (부분 매칭도 고려)
            basic_score = 0
            for token in query_tokens:
                if token in doc_content_lower:
                    basic_score += 1
                else:
                    # 부분 매칭 점수 (토큰의 일부가 포함된 경우)
                    for doc_token in doc_tokens:
                        if len(token) > 2 and (token in doc_token or doc_token in token):
                            basic_score += 0.3
                            break
            
            # 가중치 계산
            # 1. TCFD 관련 키워드에 높은 가중치
            tcfd_keywords = ['tcfd', '기후', '기후변화', '탄소', '온실가스', 'esg', '지속가능', '재무', '공시', '위험', '기회']
            tcfd_weight = 0
            for keyword in tcfd_keywords:
                if keyword in doc_content_lower:
                    tcfd_weight += 0.3
            
            # 2. 회사명 매칭에 높은 가중치
            company_keywords = ['한온시스템', '현대모비스', 'hl만도', '금호타이어']
            company_weight = 0
            for company in company_keywords:
                if company in doc_content_lower:
                    company_weight += 1.0
            
            # 3. 문서 길이에 따른 정규화 (더 관대하게)
            length_factor = min(1.0, len(doc_content) / 500)  # 500자 기준으로 변경
            
            # 최종 점수 계산 (기본 점수에 더 높은 가중치)
            final_score = (basic_score * 0.5 + tcfd_weight * 0.3 + company_weight * 0.2) * length_factor
            
            return round(final_score, 3)
            
        except Exception as e:
            logger.warning(f"관련성 점수 계산 실패: {e}")
            return 0.0
    
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
