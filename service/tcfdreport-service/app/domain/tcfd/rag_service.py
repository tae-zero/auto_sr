"""
RAG (Retrieval-Augmented Generation) 서비스
SR PDF와 TCFD 기준서 임베딩 및 검색 기능
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from shutil import rmtree
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
import pandas as pd
import os

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, base_path: str = None, chroma_path: str = None, 
                 device: str = None, force_recreate: bool = False):
        
        # 환경에 따른 경로 설정
        if base_path is None:
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                base_path = "/app/document"  # Railway 환경
            else:
                base_path = "../../document"  # 로컬 개발 환경
                
        if chroma_path is None:
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                chroma_path = "/app/chroma_db"  # Railway 환경
            else:
                chroma_path = "./chroma_db"  # 로컬 개발 환경
        self.base_path = Path(base_path)
        self.chroma_path = Path(chroma_path)
        self.chroma_path.mkdir(exist_ok=True)
        self.force_recreate = force_recreate
        
        # GPU 사용 설정 (환경변수 또는 파라미터로)
        if device is None:
            device = os.getenv("EMBEDDING_DEVICE", "cpu")
        
        # 임베딩 모델 설정 (E5 모델 최적화)
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-base",
            model_kwargs={'device': device},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 텍스트 분할기 설정 (권장 파라미터)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n## ", "\n#", "\n\n", "\n", " "]
        )
        
        # 벡터스토어 캐시
        self._vectorstores = {}
        
        logger.info(f"RAG 서비스 초기화 완료 (device: {device})")
    
    def _reset_dir(self, path: Path):
        """디렉토리 초기화 (force_recreate용)"""
        if path.exists():
            for p in path.iterdir():
                if p.is_dir(): 
                    rmtree(p)
                else: 
                    p.unlink()
        path.mkdir(parents=True, exist_ok=True)
    
    async def initialize_embeddings(self) -> bool:
        """임베딩 초기화 (서비스 시작 시 호출)"""
        try:
            logger.info("🔍 임베딩 초기화 시작")
            
            # Railway 환경에서는 기존 벡터 우선 사용
            if os.getenv("RAILWAY_ENVIRONMENT") == "true":
                logger.info("🚂 Railway 환경 감지 - 기존 벡터 우선 사용")
            
            # SR 코퍼스 생성
            await self._create_sr_corpus()
            
            # TCFD Standards 생성
            await self._create_tcfd_standards()
            
            logger.info("✅ 임베딩 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 임베딩 초기화 실패: {e}")
            return False
    
    async def _create_sr_corpus(self):
        """SR PDF 문서들을 임베딩하여 sr_corpus 생성"""
        collection_name = "sr_corpus"
        collection_path = self.chroma_path / collection_name
        
        # 중복 인덱싱 방지 (안전장치)
        if collection_path.exists() and not self.force_recreate:
            try:
                # 기존 컬렉션 로드 시도
                vectorstore = Chroma(
                    collection_name=collection_name,
                    embedding_function=self.embedding_model,
                    persist_directory=str(collection_path)
                )
                self._vectorstores[collection_name] = vectorstore
                logger.info(f"✅ 기존 {collection_name} 로드 완료 (스킵)")
                return
            except Exception as e:
                logger.warning(f"기존 {collection_name} 로드 실패, 재생성: {e}")
        
        # force_recreate 시 디렉토리 초기화
        if self.force_recreate:
            self._reset_dir(collection_path)
        
        logger.info("🔹 SR 코퍼스 생성 시작")
        documents = await self._load_pdf_documents("sr")
        
        if documents:
            vectorstore = await self._create_vectorstore(documents, collection_name)
            if vectorstore:
                self._vectorstores[collection_name] = vectorstore
                logger.info("✅ SR 코퍼스 생성 완료")
    
    async def _create_tcfd_standards(self):
        """TCFD 기준서를 임베딩하여 standards 생성"""
        collection_name = "standards"
        collection_path = self.chroma_path / collection_name
        
        # 중복 인덱싱 방지 (안전장치)
        if collection_path.exists() and not self.force_recreate:
            try:
                # 기존 컬렉션 로드 시도
                vectorstore = Chroma(
                    collection_name=collection_name,
                    embedding_function=self.embedding_model,
                    persist_directory=str(collection_path)
                )
                self._vectorstores[collection_name] = vectorstore
                logger.info(f"✅ 기존 {collection_name} 로드 완료 (스킵)")
                return
            except Exception as e:
                logger.warning(f"기존 {collection_name} 로드 실패, 재생성: {e}")
        
        # force_recreate 시 디렉토리 초기화
        if self.force_recreate:
            self._reset_dir(collection_path)
        
        logger.info("🔹 TCFD Standards 생성 시작")
        documents = await self._load_pdf_documents("tcfd")
        
        if documents:
            vectorstore = await self._create_vectorstore(documents, collection_name)
            if vectorstore:
                self._vectorstores[collection_name] = vectorstore
                logger.info("✅ TCFD Standards 생성 완료")
    
    async def _load_pdf_documents(self, pdf_dir: str) -> List[Document]:
        """PDF 문서들을 로드"""
        pdf_path = self.base_path / pdf_dir
        documents = []
        
        if not pdf_path.exists():
            logger.warning(f"PDF 디렉토리가 존재하지 않습니다: {pdf_path}")
            return documents
        
        # TCFD 매핑 로드 (있는 경우)
        tcfd_mapping = await self._load_tcfd_mapping()
        
        for pdf_file in pdf_path.glob("*.pdf"):
            try:
                logger.info(f"PDF 로딩 중: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                pages = loader.load()
                
                # 파일명에서 회사명과 연도 추출
                company, year = self._extract_company_year(pdf_file.name)
                
                # 메타데이터 추가 (개선된 버전)
                for i, page in enumerate(pages):
                    metadata = {
                        "collection": pdf_dir,
                        "source": pdf_file.name,
                        "company": company,
                        "year": year,
                        "page_from": i + 1,
                        "page_to": i + 1,
                        "type": "pdf"
                    }
                    
                    # TCFD 매핑 정보 추가 (있는 경우)
                    if tcfd_mapping and company in tcfd_mapping:
                        metadata.update(tcfd_mapping[company])
                    
                    page.metadata.update(metadata)
                
                documents.extend(pages)
                logger.info(f"✅ {pdf_file.name} 로딩 완료 ({len(pages)} 페이지)")
                
            except Exception as e:
                logger.error(f"❌ {pdf_file.name} 로딩 실패: {e}")
        
        return documents
    
    def _extract_company_year(self, filename: str) -> tuple:
        """파일명에서 회사명과 연도 추출"""
        parts = filename.replace('.pdf', '').split('_')
        
        if len(parts) >= 2:
            company = parts[0]
            year = parts[-1]
            return company, year
        
        return filename.replace('.pdf', ''), "unknown"
    
    async def _load_tcfd_mapping(self) -> Dict:
        """TCFD 매핑 정보 로드"""
        mapping_path = self.base_path / "tcfd_mapping.xlsx"
        
        if not mapping_path.exists():
            logger.info("TCFD 매핑 파일이 없습니다.")
            return {}
        
        try:
            df = pd.read_excel(mapping_path)
            mapping = {}
            
            for _, row in df.iterrows():
                company = row.get('company', '')
                if company:
                    mapping[company] = {
                        "pillar": row.get('pillar', ''),
                        "section": row.get('section', '')
                    }
            
            logger.info(f"TCFD 매핑 로드 완료: {len(mapping)}개 회사")
            return mapping
            
        except Exception as e:
            logger.error(f"TCFD 매핑 로드 실패: {e}")
            return {}
    
    async def _create_vectorstore(self, documents: List[Document], collection_name: str) -> Optional[Chroma]:
        """문서들을 임베딩하여 ChromaDB 벡터스토어 생성"""
        if not documents:
            logger.warning(f"문서가 없습니다: {collection_name}")
            return None
        
        # 텍스트 분할 (E5 모델 최적화 + 메타데이터 복사)
        logger.info(f"텍스트 분할 중: {collection_name}")
        texts = []
        metadatas = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc.page_content)
            for chunk in chunks:
                # E5 모델 최적화: 문서에 "passage: " 프리픽스 추가
                optimized_text = f"passage: {chunk}"
                texts.append(optimized_text)
                # 메타데이터 복사본 생성 (dict 레퍼런스 재사용 방지)
                metadatas.append(dict(doc.metadata))
        
        logger.info(f"✅ {collection_name}: {len(texts)}개 청크 생성")
        
        # ChromaDB 벡터스토어 생성
        vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embedding_model,
            metadatas=metadatas,
            collection_name=collection_name,
            persist_directory=str(self.chroma_path / collection_name)
        )
        
        # 저장
        vectorstore.persist()
        logger.info(f"✅ {collection_name} 벡터스토어 생성 및 저장 완료")
        
        return vectorstore
    
    async def search_sr_corpus(self, query: str, k: int = 5, filters: Dict = None) -> List[Document]:
        """SR 코퍼스에서 검색"""
        if "sr_corpus" not in self._vectorstores:
            logger.error("SR 코퍼스가 초기화되지 않았습니다.")
            return []
        
        try:
            # E5 모델 최적화: 쿼리에 "query: " 프리픽스 추가
            q = f"query: {query}"
            results = self._vectorstores["sr_corpus"].similarity_search(
                q, 
                k=k,
                filter=filters
            )
            logger.info(f"SR 코퍼스 검색 완료: {len(results)}개 결과")
            return results
        except Exception as e:
            logger.error(f"SR 코퍼스 검색 실패: {e}")
            return []
    
    async def search_standards(self, query: str, k: int = 5, filters: Dict = None) -> List[Document]:
        """TCFD Standards에서 검색"""
        if "standards" not in self._vectorstores:
            logger.error("TCFD Standards가 초기화되지 않았습니다.")
            return []
        
        try:
            # E5 모델 최적화: 쿼리에 "query: " 프리픽스 추가
            q = f"query: {query}"
            results = self._vectorstores["standards"].similarity_search(
                q, 
                k=k,
                filter=filters
            )
            logger.info(f"TCFD Standards 검색 완료: {len(results)}개 결과")
            return results
        except Exception as e:
            logger.error(f"TCFD Standards 검색 실패: {e}")
            return []
    
    async def search_all(self, query: str, k: int = 5, filters: Dict = None) -> Dict[str, List[Document]]:
        """모든 컬렉션에서 검색"""
        results = {
            "sr_corpus": await self.search_sr_corpus(query, k, filters),
            "standards": await self.search_standards(query, k, filters)
        }
        return results
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """컬렉션 정보 조회"""
        info = {}
        
        for collection_name, vectorstore in self._vectorstores.items():
            try:
                # ChromaDB 클라이언트로 컬렉션 정보 조회
                chroma_path = str(self.chroma_path / collection_name)
                client = chromadb.PersistentClient(path=chroma_path)
                collection = client.get_collection(name=collection_name)
                count = collection.count()
                
                info[collection_name] = {
                    "document_count": count,
                    "status": "active"
                }
                
            except Exception as e:
                logger.warning(f"{collection_name} 정보 조회 실패: {e}")
                info[collection_name] = {
                    "document_count": 0,
                    "status": "error"
                }
        
        return info
    
    async def close(self):
        """리소스 정리"""
        logger.info("RAG 서비스 리소스 정리")
        self._vectorstores.clear()
