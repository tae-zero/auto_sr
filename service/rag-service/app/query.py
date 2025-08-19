from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Set, Tuple
from pathlib import Path
from .embeddings import embeddings
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from .config import FAISS_DIR, LLM_BACKEND, BASE_MODEL, OPENAI_API_KEY, QUANTIZE
from .vectorstore import retriever, collection_path

# ---- LLM 지연 로드 & 캐시 ----
_LLM = None
def get_llm():
    global _LLM
    if _LLM is not None:
        return _LLM

    if LLM_BACKEND == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY 미설정")
        from langchain_openai import ChatOpenAI
        _LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        return _LLM

    # ---- HF 로컬 모델 (Polyglot 3.8B) ----
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from langchain_community.llms import HuggingFacePipeline

    tok = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tok.pad_token is None and tok.eos_token is not None:
        tok.pad_token = tok.eos_token

    load_kwargs = {"device_map": "auto", "torch_dtype": "auto"}
    if QUANTIZE == "8bit":
        load_kwargs["load_in_8bit"] = True
    elif QUANTIZE == "4bit":
        load_kwargs["load_in_4bit"] = True

    mdl = AutoModelForCausalLM.from_pretrained(BASE_MODEL, **load_kwargs)

    gen = pipeline(
        "text-generation",
        model=mdl,
        tokenizer=tok,
        max_new_tokens=512,
        do_sample=False,
        return_full_text=False,  # 프롬프트 제외
        pad_token_id=tok.eos_token_id,
    )
    _LLM = HuggingFacePipeline(pipeline=gen)
    return _LLM

PROMPT = PromptTemplate.from_template(
    """당신은 ESG/TCFD 전문가입니다.
사용자 질문: {question}

아래 컨텍스트만을 근거로 간결하고 정확한 한국어 답변을 작성하세요.
가능하면 근거의 출처(회사/연도/페이지)도 함께 제시하세요.

[컨텍스트]
{context}

[규칙]
- 답변에 추측을 넣지 마세요.
- 컨텍스트에 없는 내용은 "제공된 자료 기준으로 확인되지 않습니다."라고 말하세요.

답변:"""
)

router = APIRouter(prefix="/rag", tags=["RAG"])

class QueryReq(BaseModel):
    question: str
    top_k: int = 5
    collections: List[str] = ["sr_corpus", "standards"]

def _dedup_docs(docs: List[Document]) -> List[Document]:
    seen: Set[Tuple[str, str]] = set()
    uniq: List[Document] = []
    for d in docs:
        m = d.metadata or {}
        key = (str(m.get("source")), str(m.get("page_from")))
        if key in seen:
            continue
        seen.add(key)
        uniq.append(d)
    return uniq

@router.post("/query")
def query(req: QueryReq):
    # 1) 컬렉션 경로 확인
    paths = []
    for c in req.collections:
        p = collection_path(c)
        if not ((p / "index.faiss").exists() and (p / "index.pkl").exists()):
            raise HTTPException(404, f"FAISS 인덱스가 없습니다: {p}")
        paths.append(p)

    # 2) 컬렉션별 검색
    k = max(1, req.top_k)
    per = max(1, k // len(paths))
    docs: List[Document] = []
    for p in paths:
        r = retriever(p, k=per)
        docs.extend(r.invoke(req.question))     # ✅ 최신 권장

    docs = _dedup_docs(docs)

    # 부족분 보충
    if len(docs) < k:
        r0 = retriever(paths[0], k=k)
        extra = _dedup_docs(r0.invoke(req.question))
        have = {(str(d.metadata.get("source")), str(d.metadata.get("page_from"))) for d in docs}
        for d in extra:
            key = (str(d.metadata.get("source")), str(d.metadata.get("page_from")))
            if key not in have:
                docs.append(d)
                have.add(key)
            if len(docs) >= k:
                break

    docs = docs[:k]

    # 3) 컨텍스트
    def fmt(d: Document):
        m = d.metadata or {}
        src = f"{m.get('company','?')} {m.get('year','?')} p.{m.get('page_from','?')}"
        return f"[{src}] {d.page_content.strip()}"
    context = "\n\n".join(fmt(d) for d in docs)

    # 4) 생성
    llm = get_llm()
    prompt = PROMPT.format(question=req.question, context=context)
    answer = llm(prompt)

    # 5) 참고 메타
    refs: List[Dict] = []
    for d in docs:
        m = d.metadata or {}
        refs.append({
            "source": m.get("source"),
            "company": m.get("company"),
            "year": m.get("year"),
            "page_from": m.get("page_from"),
            "page_to": m.get("page_to"),
            "collection": m.get("collection"),
        })

    return {"answer": str(answer), "refs": refs}
