#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG 임베딩 서비스 (pgvector 전용)
- document/sr, document/tcfd 임베딩 → Postgres(pgvector)에 저장
- Chroma/FAISS 코드 없음
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import pandas as pd

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector
from langchain.document_loaders import PyPDFLoader

# ---------- 경로/환경 ----------
PROJECT_ROOT = Path(__file__).resolve().parents[1]              # C:\taezero\auto_sr
BASE_PATH = PROJECT_ROOT / "document"
SR_DIR = BASE_PATH / "sr"
TCFD_DIR = BASE_PATH / "tcfd"

PG_CONN_STR = os.getenv("PG_CONN_STR", "")  # ex) postgresql+psycopg://user:pwd@host:5432/db?sslmode=require

# ---------- 로깅 ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("rag_pgvector")

# ---------- 임베딩 모델 ----------
EMBED_MODEL_NAME = "intfloat/multilingual-e5-base"
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL_NAME,
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# ---------- 텍스트 분할 ----------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    length_function=len,
    separators=["\n## ", "\n#", "\n\n", "\n", " "]
)

# ---------- 유틸 ----------
def extract_company_year(filename: str) -> Tuple[str, str]:
    """파일명 '회사명_연도.pdf' 형태에서 회사/연도 추출"""
    name = filename.replace(".pdf", "")
    parts = name.split("_")
    if len(parts) >= 2:
        return parts[0], parts[-1]
    return name, "unknown"

def load_tcfd_mapping() -> Dict[str, Dict[str, str]]:
    """
    TCFD 매핑: document/TCFD_MAPPING_FINAL.xlsx 를 읽어
    company 키로 대표 레코드를 1개씩 저장.
    필요한 필드만 남기고 컬럼명 정규화.
    """
    xls = BASE_PATH / "TCFD_MAPPING_FINAL.xlsx"
    if not xls.exists():
        logger.info("TCFD 매핑 파일이 없습니다. (건너뜀)")
        return {}
    try:
        df = pd.read_excel(xls)

        # 엑셀에서 잘린 컬럼명 보정
        rename_map = {'...on': 'description'}
        df = df.rename(columns=rename_map)

        # 필요 컬럼 확보
        needed = ['company', 'year', 'pillar', 'section_tag',
                  'tcfd_section', 'requirement_id', 'page_from', 'page_to']
        for col in needed:
            if col not in df.columns:
                df[col] = None

        # 회사별 대표 1행 (여러 개면 마지막)
        df = df.sort_index()
        grouped = df.groupby('company', dropna=True).tail(1)

        mapping: Dict[str, Dict[str, str]] = {}
        for _, r in grouped.iterrows():
            company = str(r.get('company') or '').strip()
            if not company:
                continue
            mapping[company] = {
                'pillar': str(r.get('pillar') or ''),
                'section_tag': str(r.get('section_tag') or ''),
                'tcfd_section': str(r.get('tcfd_section') or ''),
                'requirement_id': str(r.get('requirement_id') or ''),
                'mapped_page_from': str(r.get('page_from') or ''),
                'mapped_page_to': str(r.get('page_to') or ''),
                'mapping_year': str(r.get('year') or ''),
            }
        logger.info(f"TCFD 매핑 로드 완료: {len(mapping)}개 회사")
        return mapping
    except Exception as e:
        logger.error(f"TCFD 매핑 로드 실패: {e}")
        return {}

def load_pdf_dir(pdf_dir: Path) -> List[Any]:
    """PDF 디렉토리를 페이지 단위 Document 리스트로 변환(+메타)"""
    docs: List[Any] = []
    if not pdf_dir.exists():
        logger.error(f"PDF 디렉토리가 존재하지 않습니다: {pdf_dir}")
        return docs

    tcfd_map = load_tcfd_mapping()

    for pdf in pdf_dir.glob("*.pdf"):
        try:
            logger.info(f"PDF 로딩 중: {pdf.name}")
            pages = PyPDFLoader(str(pdf)).load()
            company, year = extract_company_year(pdf.name)
            for i, page in enumerate(pages):
                meta = {
                    "collection": pdf_dir.name,
                    "source": pdf.name,
                    "company": company,
                    "year": year,
                    "page_from": i + 1,
                    "page_to": i + 1,
                    "type": "pdf",
                }
                # 매핑 정보 병합 (존재 시)
                if company in tcfd_map:
                    meta.update(tcfd_map[company])
                page.metadata.update(meta)
            docs.extend(pages)
            logger.info(f"✅ {pdf.name} 로딩 완료 ({len(pages)} 페이지)")
        except Exception as e:
            logger.error(f"❌ {pdf.name} 로딩 실패: {e}")
    return docs

def split_docs(docs: List[Any]) -> Tuple[List[str], List[Dict[str, Any]]]:
    """LangChain Document 리스트를 청크 텍스트/메타로 변환"""
    texts, metas = [], []
    for d in docs:
        chunks = text_splitter.split_text(d.page_content)
        for c in chunks:
            texts.append(c)
            metas.append(dict(d.metadata))
    return texts, metas

# ---------- 저장 ----------
def upsert_pgvector(texts: List[str], metadatas: List[Dict[str, Any]], collection_name: str):
    """pgvector(Postgres)에 업서트"""
    if not PG_CONN_STR:
        raise SystemExit("PG_CONN_STR 환경변수를 설정하세요. (pgvector Postgres 접속 문자열)")
    PGVector.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name=collection_name,
        connection_string=PG_CONN_STR,
    )
    logger.info(f"✅ pgvector 업서트 완료: collection={collection_name}, chunks={len(texts)}")

def build_collection(pdf_dir: Path, collection_name: str):
    docs = load_pdf_dir(pdf_dir)
    if not docs:
        logger.warning(f"문서가 없습니다: {collection_name}")
        return
    texts, metas = split_docs(docs)
    logger.info(f"✅ {collection_name}: {len(texts)}개 청크 생성")
    upsert_pgvector(texts, metas, collection_name)

def main():
    logger.info("🚀 pgvector 임베딩 업서트 시작")
    build_collection(SR_DIR, "sr_corpus")
    build_collection(TCFD_DIR, "standards")
    logger.info("🎉 완료")

if __name__ == "__main__":
    main()
