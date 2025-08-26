"""
RAG (Retrieval-Augmented Generation) 도메인

FAISS 인덱스를 통한 정보 검색 및 관련 문서 제공 기능을 제공합니다.
"""

from .rag_service import RAGService

__all__ = [
    "RAGService"
]
