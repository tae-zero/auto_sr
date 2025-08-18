#!/usr/bin/env python3
"""
임베딩 테스트 스크립트
생성된 ChromaDB 벡터스토어를 테스트
"""

import logging
from pathlib import Path
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_embeddings():
    """임베딩 테스트"""
    chroma_path = Path("chroma_db")
    
    if not chroma_path.exists():
        logger.error("ChromaDB 디렉토리가 존재하지 않습니다.")
        return
    
    # 임베딩 모델 로드
    embedding_model = HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-base",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 테스트할 컬렉션들
    collections = ["sr_corpus", "standards"]
    
    for collection_name in collections:
        collection_path = chroma_path / collection_name
        
        if not collection_path.exists():
            logger.warning(f"컬렉션이 존재하지 않습니다: {collection_name}")
            continue
        
        logger.info(f"🔍 {collection_name} 테스트 시작")
        
        try:
            # 벡터스토어 로드
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=embedding_model,
                persist_directory=str(collection_path)
            )
            
            # 검색 테스트
            test_queries = [
                "기후변화",
                "ESG",
                "지속가능성",
                "탄소배출",
                "거버넌스"
            ]
            
            for query in test_queries:
                logger.info(f"  검색어: '{query}'")
                results = vectorstore.similarity_search(query, k=2)
                
                for i, result in enumerate(results):
                    source = result.metadata.get('source', 'Unknown')
                    page = result.metadata.get('page', 'N/A')
                    content_preview = result.page_content[:100] + "..."
                    
                    logger.info(f"    결과 {i+1}: {source} (페이지: {page})")
                    logger.info(f"    내용: {content_preview}")
                
                logger.info("")
            
            logger.info(f"✅ {collection_name} 테스트 완료")
            
        except Exception as e:
            logger.error(f"❌ {collection_name} 테스트 실패: {e}")
        
        logger.info("-" * 50)

def main():
    """메인 실행 함수"""
    logger.info("🚀 임베딩 테스트 시작")
    test_embeddings()
    logger.info("🎉 임베딩 테스트 완료")

if __name__ == "__main__":
    main()
