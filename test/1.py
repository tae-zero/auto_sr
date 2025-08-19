#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FAISS 인덱스 빌더 (단일/다중 PDF)
- 입력: PDF 경로(들)
- 출력: vectordb/<collection>/index.faiss, index.pkl
- 임베딩: intfloat/multilingual-e5-base (코사인 정규화)
- 검색타입: COSINE
"""

import os
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Any

import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS, DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings

# ---------- 경로/환경 ----------
PROJECT_ROOT = Path(__file__).resolve().parent
VECTORDIR = PROJECT_ROOT / "vectordb" / "demo"   # <- 저장될 경로(원하면 변경)
VECTORDIR.mkdir(parents=True, exist_ok=True)

# PDF 예시: 업로드 파일 경로
# - 로컬 테스트 시: PDF_PATHS = ["./document/sr/삼성전자_2024.pdf", "./document/tcfd/TCFD.pdf"]
# - 본 요청 파일: /mnt/data/정태영.pdf
PDF_PATHS = ["정태영.pdf"]  # 필요시 여러 개 추가 가능

# ---------- 로깅 ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("faiss_builder")

# ---------- 임베딩 ----------
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "intfloat/multilingual-e5-base")
EMBED_DEVICE = os.environ.get("EMBED_DEVICE", "cuda")  # "cuda" or "cpu"
EMBED_BATCH_SIZE = int(os.environ.get("EMBED_BATCH_SIZE", "16"))

embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL_NAME,
    model_kwargs={"device": EMBED_DEVICE},
    encode_kwargs={
        "normalize_embeddings": True,
        "batch_size": EMBED_BATCH_SIZE,
    },
)

# ---------- 텍스트 분할 ----------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n## ", "\n#", "\n\n", "\n", " "],
)

def extract_company_year(filename: str) -> Tuple[str, str]:
    """파일명 '회사명_연도.pdf' → (회사명, 연도) 간단 추출"""
    base = Path(filename).name.replace(".pdf", "")
    parts = base.split("_")
    if len(parts) >= 2:
        return parts[0], parts[-1]
    return base, "unknown"

def load_pdfs(pdf_paths: List[str]) -> List[Any]:
    """PDF들을 LangChain Documents로 로드(페이지 단위), 기본 메타 추가"""
    docs = []
    for p in pdf_paths:
        pth = Path(p)
        if not pth.exists():
            log.warning(f"PDF 없음: {pth}")
            continue
        try:
            log.info(f"PDF 로딩: {pth.name}")
            pages = PyPDFLoader(str(pth)).load()
            company, year = extract_company_year(pth.name)
            for i, page in enumerate(pages):
                meta = {
                    "source": pth.name,
                    "company": company,
                    "year": year,
                    "page_from": i+1,
                    "page_to": i+1,
                    "type": "pdf",
                    "collection": "demo",
                }
                page.metadata.update(meta)
            docs.extend(pages)
            log.info(f"  -> {pth.name} {len(pages)} pages")
        except Exception as e:
            log.error(f"로딩 실패({pth.name}): {e}")
    return docs

def split_docs(docs) -> Tuple[List[str], List[Dict[str, Any]]]:
    texts, metas = [], []
    for d in docs:
        chunks = text_splitter.split_text(d.page_content or "")
        for c in chunks:
            c_strip = c.strip()
            if not c_strip:
                continue
            texts.append(c_strip)
            metas.append(dict(d.metadata))
    return texts, metas

def upsert_faiss(texts: List[str], metas: List[Dict[str, Any]], save_dir: Path):
    save_dir.mkdir(parents=True, exist_ok=True)
    idx_file = save_dir / "index.faiss"
    pkl_file = save_dir / "index.pkl"

    if idx_file.exists() and pkl_file.exists():
        store = FAISS.load_local(
            str(save_dir), embeddings,
            allow_dangerous_deserialization=True,
            distance_strategy=DistanceStrategy.COSINE,
        )
        store.add_texts(texts, metadatas=metas)
        store.save_local(str(save_dir))
        log.info(f"🔁 추가 저장: +{len(texts)} chunks → {save_dir}")
    else:
        store = FAISS.from_texts(
            texts,
            embeddings,
            metadatas=metas,
            distance_strategy=DistanceStrategy.COSINE,
        )
        store.save_local(str(save_dir))
        log.info(f"🆕 신규 인덱스 생성: chunks={len(texts)} → {save_dir}")

def main():
    log.info(f"🚀 FAISS 빌드 시작 (device={EMBED_DEVICE}, model={EMBED_MODEL_NAME}, batch={EMBED_BATCH_SIZE})")
    docs = load_pdfs(PDF_PATHS)
    if not docs:
        log.error("문서가 없습니다. 종료.")
        return
    texts, metas = split_docs(docs)
    log.info(f"총 청크: {len(texts)}")
    if not texts:
        log.error("빈 청크. 종료.")
        return
    upsert_faiss(texts, metas, VECTORDIR)

    # 간단 유사도 검색 테스트
    try:
        store = FAISS.load_local(
            str(VECTORDIR), embeddings,
            allow_dangerous_deserialization=True,
            distance_strategy=DistanceStrategy.COSINE,
        )
        test_q = "전북 현대의 최근 성적"
        results = store.similarity_search(test_q, k=3)
        log.info(f"[검색테스트] '{test_q}' top-3")
        for i, r in enumerate(results, 1):
            m = r.metadata or {}
            log.info(f" {i}. {m.get('source')} p.{m.get('page_from')} | {r.page_content[:80]}...")
    except Exception as e:
        log.warning(f"검색테스트 실패: {e}")

    log.info(f"🎉 완료. 저장 위치: {VECTORDIR} (index.faiss, index.pkl)")

if __name__ == "__main__":
    main()
