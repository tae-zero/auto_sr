#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --- env 로딩 (.env는 OPENAI_API_KEY=sk-... 형식, 따옴표/공백 X) ---
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=False)

import os
from pathlib import Path
from typing import List

from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS, DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import Document

# ---------- 설정 ----------
VECTORDIR = Path(__file__).resolve().parent / "vectordb" / "demo"

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")  # 필요시 gpt-4.1-mini 등
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 임베딩 설정(E5 유지)
EMBED_MODEL_NAME = os.environ.get("EMBED_MODEL_NAME", "intfloat/multilingual-e5-base")
EMBED_DEVICE     = os.environ.get("EMBED_DEVICE", "cuda")  # "cuda" or "cpu"
EMBED_BATCH_SIZE = int(os.environ.get("EMBED_BATCH_SIZE", "16"))

# ---------- 사전 검증 ----------
if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith("sk-"):
    raise RuntimeError(
        "OPENAI_API_KEY가 설정되지 않았습니다. .env에 'OPENAI_API_KEY=sk-...' 형식으로 저장하고 다시 실행하세요."
    )

# ---------- 임베딩 ----------
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL_NAME,
    model_kwargs={"device": EMBED_DEVICE},
    encode_kwargs={"normalize_embeddings": True, "batch_size": EMBED_BATCH_SIZE},
)

def load_store() -> FAISS:
    if not (VECTORDIR / "index.faiss").exists():
        raise FileNotFoundError(f"FAISS 인덱스가 없습니다: {VECTORDIR} (index.faiss, index.pkl 확인)")
    return FAISS.load_local(
        str(VECTORDIR),
        embeddings,
        allow_dangerous_deserialization=True,
        distance_strategy=DistanceStrategy.COSINE,
    )

def pretty_ctx(docs: List[Document], max_chars: int = 240) -> str:
    out = []
    for i, d in enumerate(docs, 1):
        m = d.metadata or {}
        head = f"[{i}] {m.get('source', 'unknown')} p.{m.get('page_from', '?')}"
        body = (d.page_content or "").replace("\n", " ").strip()
        if len(body) > max_chars:
            body = body[:max_chars] + "..."
        out.append(f"{head}\n  {body}")
    return "\n".join(out)

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
    # 1) 인덱스 로드 & 리트리버
    store = load_store()

    # 최신 권장 방식: get_relevant_documents() 대신 invoke() 사용
    retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    # retriever = store.as_retriever(search_type="mmr", search_kwargs={"k": 4, "fetch_k": 15, "lambda_mult": 0.4})

    # 2) 검색 예제
    query = "이 글에서 나온 축구선수들의 이름은??"
    docs: List[Document] = retriever.invoke(query)   # ✅ LangChain 0.1.46+ 권장

    print("=== [검색 결과 top-3] ===")
    print(pretty_ctx(docs), "\n")

    # 3) OpenAI LLM 준비
    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0.2)

    # 4) RAG 프롬프트 구성 & 호출
    ctx_text = pretty_ctx(docs, max_chars=800)
    prompt = make_prompt(query, ctx_text)
    ans = llm.invoke(prompt)

    print("=== [RAG 답변] ===")
    print(ans.content)

if __name__ == "__main__":
    main()
