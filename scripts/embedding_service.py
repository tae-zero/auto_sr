#!/usr/bin/env python3
"""
RAG 임베딩 서비스
SR PDF와 TCFD 기준서를 임베딩하여 ChromaDB에 저장
"""
## pgvector 

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
import pandas as pd
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGEmbeddingService:
    def __init__(self, base_path: str = "document"):
        self.base_path = Path(base_path)
        self.chroma_path = Path("chroma_db")
        self.chroma_path.mkdir(exist_ok=True)
        
        # 임베딩 모델 설정
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-base",
            model_kwargs={'device': 'cpu'},  # GPU 사용 시 'cuda'로 변경
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 텍스트 분할기 설정 (권장 파라미터)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n## ", "\n#", "\n\n", "\n", " "]
        )
        
        logger.info("RAG 임베딩 서비스 초기화 완료")
    
    def load_pdf_documents(self, pdf_dir: str) -> List[Dict[str, Any]]:
        """PDF 문서들을 로드하고 청크로 분할"""
        pdf_path = self.base_path / pdf_dir
        documents = []
        
        if not pdf_path.exists():
            logger.error(f"PDF 디렉토리가 존재하지 않습니다: {pdf_path}")
            return documents
        
        # TCFD 매핑 로드 (있는 경우)
        tcfd_mapping = self.load_tcfd_mapping()
        
        for pdf_file in pdf_path.glob("*.pdf"):
            try:
                logger.info(f"PDF 로딩 중: {pdf_file.name}")
                loader = PyPDFLoader(str(pdf_file))
                pages = loader.load()
                
                # 파일명에서 회사명과 연도 추출
                company, year = self.extract_company_year(pdf_file.name)
                
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
    
    def extract_company_year(self, filename: str) -> tuple:
        """파일명에서 회사명과 연도 추출"""
        # 파일명 패턴: 회사명_연도.pdf
        parts = filename.replace('.pdf', '').split('_')
        
        if len(parts) >= 2:
            company = parts[0]
            year = parts[-1]  # 마지막 부분이 연도
            return company, year
        
        return filename.replace('.pdf', ''), "unknown"
    
    def load_tcfd_mapping(self) -> Dict:
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
    
    def load_excel_documents(self, excel_file: str) -> List[Dict[str, Any]]:
        """Excel 파일을 로드하고 청크로 분할"""
        excel_path = self.base_path / excel_file
        
        if not excel_path.exists():
            logger.error(f"Excel 파일이 존재하지 않습니다: {excel_path}")
            return []
        
        try:
            logger.info(f"Excel 로딩 중: {excel_file}")
            df = pd.read_excel(excel_path)
            
            documents = []
            for idx, row in df.iterrows():
                # 각 행을 문서로 변환
                content = ""
                metadata = {"source": excel_file, "type": "excel", "row": idx + 1}
                
                for col in df.columns:
                    if pd.notna(row[col]):
                        content += f"{col}: {row[col]}\n"
                        metadata[col] = str(row[col])
                
                if content.strip():
                    documents.append({
                        "page_content": content.strip(),
                        "metadata": metadata
                    })
            
            logger.info(f"✅ {excel_file} 로딩 완료 ({len(documents)} 행)")
            return documents
            
        except Exception as e:
            logger.error(f"❌ {excel_file} 로딩 실패: {e}")
            return []
    
    def create_vectorstore(self, documents: List[Dict[str, Any]], collection_name: str) -> Chroma:
        """문서들을 임베딩하여 ChromaDB 벡터스토어 생성"""
        if not documents:
            logger.warning(f"문서가 없습니다: {collection_name}")
            return None
        
        # 텍스트 분할
        logger.info(f"텍스트 분할 중: {collection_name}")
        texts = []
        metadatas = []
        
        for doc in documents:
            if hasattr(doc, 'page_content'):
                # LangChain Document 객체
                chunks = self.text_splitter.split_text(doc.page_content)
                for chunk in chunks:
                    texts.append(chunk)
                    metadatas.append(doc.metadata)
            else:
                # 딕셔너리 형태
                chunks = self.text_splitter.split_text(doc["page_content"])
                for chunk in chunks:
                    texts.append(chunk)
                    metadatas.append(doc["metadata"])
        
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
    
    def create_sr_corpus(self):
        """SR PDF 문서들을 임베딩하여 sr_corpus 생성"""
        logger.info("🔹 SR 코퍼스 생성 시작")
        
        # SR PDF 문서 로드
        documents = self.load_pdf_documents("sr")
        
        if documents:
            # 벡터스토어 생성
            vectorstore = self.create_vectorstore(documents, "sr_corpus")
            
            if vectorstore:
                # 검색 테스트
                results = vectorstore.similarity_search("기후변화", k=3)
                logger.info(f"✅ SR 코퍼스 검색 테스트 성공: {len(results)}개 결과")
        
        logger.info("🔹 SR 코퍼스 생성 완료")
    
    def create_tcfd_standards(self):
        """TCFD 기준서를 임베딩하여 standards 생성"""
        logger.info("🔹 TCFD Standards 생성 시작")
        
        # TCFD 기준서 PDF 로드
        documents = self.load_pdf_documents("tcfd")
        
        if documents:
            # 벡터스토어 생성 (chroma_db/standards)
            vectorstore = self.create_vectorstore(documents, "standards")
            
            if vectorstore:
                # 검색 테스트
                results = vectorstore.similarity_search("거버넌스", k=3)
                logger.info(f"✅ TCFD Standards 검색 테스트 성공: {len(results)}개 결과")
        
        logger.info("🔹 TCFD Standards 생성 완료")
    
    def create_all_embeddings(self):
        """모든 임베딩 생성"""
        logger.info("🚀 전체 임베딩 프로세스 시작")
        
        # SR 코퍼스 생성
        self.create_sr_corpus()
        
        # TCFD Standards 생성
        self.create_tcfd_standards()
        
        logger.info("🎉 전체 임베딩 프로세스 완료!")
        
        # 저장된 컬렉션 정보 출력
        self.print_collection_info()
    
    def print_collection_info(self):
        """저장된 컬렉션 정보 출력"""
        logger.info("📊 저장된 컬렉션 정보:")
        
        for collection_dir in self.chroma_path.iterdir():
            if collection_dir.is_dir():
                collection_name = collection_dir.name
                chroma_path = str(collection_dir)
                
                try:
                    # ChromaDB 클라이언트로 컬렉션 정보 조회
                    client = chromadb.PersistentClient(path=chroma_path)
                    collection = client.get_collection(name=collection_name)
                    count = collection.count()
                    
                    logger.info(f"  - {collection_name}: {count}개 문서")
                    
                except Exception as e:
                    logger.warning(f"  - {collection_name}: 정보 조회 실패 ({e})")

def main():
    """메인 실행 함수"""
    service = RAGEmbeddingService()
    service.create_all_embeddings()

if __name__ == "__main__":
    main()
