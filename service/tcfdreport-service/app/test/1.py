#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FAISS 인덱스 검증용 RAG 스크립트
- 사용법:
  python rag_verify.py --collection sr_corpus --query "기후변화 영향"
  python rag_verify.py --collection standards --query "거버넌스 요구사항 요약"

- 기능:
  1) FAISS 인덱스 로드 → retriever.invoke()로 top-k 검색 결과 출력
  2) (선택) OPENAI_API_KEY가 설정되어 있으면 ChatOpenAI로 RAG 답변 생성
"""

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=False)

import os
import argparse
from pathlib import Path
from typing import List

from langchain_community.vectorstores import FAISS, DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

# (선택) OpenAI 사용
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))
if USE_OPENAI:
    from langchain_openai import ChatOpenAI

# ---------- 경로 설정: 빌더와 동일한 폴더 구조 ----------
# PROJECT_ROOT = Path(__file__).resolve().parents[1]                    # C:\taezero\auto_sr
FAISS_DIR = Path(__file__).resolve().parents[2] / "vectordb"

# ---------- 임베딩 설정(E5-base, cosine 정규화) ----------
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "intfloat/multilingual-e5-base")
EMBED_DEVICE     = os.environ.get("EMBED_DEVICE", "cuda")  # cuda / cpu
EMBED_BATCH_SIZE = int(os.environ.get("EMBED_BATCH_SIZE", "16"))

embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL_NAME,
    model_kwargs={"device": EMBED_DEVICE},
    encode_kwargs={"normalize_embeddings": True, "batch_size": EMBED_BATCH_SIZE},
)

def load_store(collection: str) -> FAISS:
    path = FAISS_DIR / collection
    if not (path / "index.faiss").exists():
        raise FileNotFoundError(f"인덱스 파일이 없습니다: {path} (index.faiss, index.pkl 확인)")
    return FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True,
        distance_strategy=DistanceStrategy.COSINE,
    )

def pretty_ctx(docs: List[Document], max_chars: int = 240) -> str:
    lines = []
    for i, d in enumerate(docs, 1):
        m = d.metadata or {}
        src = m.get("source", "unknown")
        p   = m.get("page_from", "?")
        body = (d.page_content or "").replace("\n", " ").strip()
        if len(body) > max_chars:
            body = body[:max_chars] + "..."
        lines.append(f"[{i}] {src} p.{p}\n  {body}")
    return "\n".join(lines)

def make_prompt(query: str, ctx: str) -> str:
    return f"""당신은 문서 기반 QA 어시스턴트입니다.
아래 컨텍스트를 참고하여 질문에 한국어로 간결하고 정확하게 답하세요.
컨텍스트에 없는 내용은 추측하지 말고 '문서에서 확인되지 않습니다'라고 답하세요.

[컨텍스트]
{ctx}

[질문]
{query}

[요구사항]
- 컨텍스트에 근거한 사실만 답변
- 필요시 (출처: 파일명 p.페이지) 형태로 간단히 근거 표시
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", required=True, choices=["sr_corpus", "standards"],
                        help="조회할 벡터 컬렉션 이름")
    parser.add_argument("--query", required=True, help="질문 문장")
    parser.add_argument("--k", type=int, default=3, help="가져올 문서 수")
    parser.add_argument("--mmr", action="store_true", help="MMR 다양성 검색 사용")
    args = parser.parse_args()

    # 1) 벡터 스토어 로드
    store = load_store(args.collection)

    # 2) 리트리버 설정 (similarity 또는 MMR)
    if args.mmr:
        retriever = store.as_retriever(search_type="mmr",
                                       search_kwargs={"k": args.k, "fetch_k": max(10, args.k*4), "lambda_mult": 0.4})
    else:
        retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": args.k})

    # 3) 검색 실행 (LangChain 최신 권장: invoke)
    docs: List[Document] = retriever.invoke(args.query)

    print("=== [검색 결과 top-{} from '{}'] ===".format(args.k, args.collection))
    print(pretty_ctx(docs), "\n")

    # 4) (선택) OpenAI로 RAG 답변
    if USE_OPENAI:
        model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(model=model_name, temperature=0.2)
        ctx_text = pretty_ctx(docs, max_chars=800)
        prompt = make_prompt(args.query, ctx_text)
        ans = llm.invoke(prompt)
        print("=== [RAG 답변] ===")
        print(ans.content)
    else:
        print("[알림] OPENAI_API_KEY가 없어 RAG 답변 생성을 건너뜁니다. (검색 결과만 출력)")

if __name__ == "__main__":
    main()
