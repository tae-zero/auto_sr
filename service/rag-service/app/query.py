# app/query.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Set, Tuple
from pathlib import Path

from langchain.prompts import PromptTemplate
from langchain.schema import Document

from .config import LLM_BACKEND, BASE_MODEL, OPENAI_API_KEY
from .vectorstore import retriever, collection_path

# ---- LLM 지연 로드 & 캐시 ----
_LLM = None

def get_llm():
    """
    로컬 HF 모델(예: Polyglot 3.8B) 또는 OpenAI 백엔드를 LLM로 래핑해서 반환.
    - Windows 호환성/안정성을 위해 device_map/accelerate 없이 단일 GPU 직접 지정.
    - 빈 응답 이슈를 줄이기 위해 샘플링/토큰 파라미터 튜닝.
    """
    global _LLM
    if _LLM is not None:
        return _LLM

    if LLM_BACKEND == "openai":
        from langchain_openai import ChatOpenAI
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY 미설정")
        _LLM = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        return _LLM

    import os, torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from langchain_community.llms import HuggingFacePipeline

    # 약간의 성능 튜닝
    try:
        torch.set_float32_matmul_precision("high")
        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
    except Exception:
        pass

    tok = AutoTokenizer.from_pretrained(BASE_MODEL)
    if tok.pad_token is None and tok.eos_token is not None:
        tok.pad_token = tok.eos_token

    # 단일 GPU 직접 지정 (accelerate/device_map 없이)
    device = 0 if torch.cuda.is_available() else -1

    mdl = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype="auto",
    )
    if device >= 0:
        mdl = mdl.to("cuda")

    # ✅ 샘플링/최소 토큰/반복 패널티 설정 (빈 응답 방지에 도움)
    gen = pipeline(
        "text-generation",
        model=mdl,
        tokenizer=tok,
        max_new_tokens=256,         # 상한
        min_new_tokens=32,          # ✅ 최소 생성 보장
        do_sample=True,             # ✅ 확률적 디코딩
        temperature=0.7,            # ✅ 적당한 창의성
        top_p=0.9,                  # ✅ nucleus
        repetition_penalty=1.05,    # ✅ 공백/반복 억제
        return_full_text=False,
        pad_token_id=tok.eos_token_id,
        device=device,
    )

    _LLM = HuggingFacePipeline(pipeline=gen)
    return _LLM


# ✅ 지시형 + 출력 포맷을 명확히 한 프롬프트
PROMPT = PromptTemplate.from_template(
    """다음은 한국어 지시문과 근거 컨텍스트입니다. 지시를 따르고, 근거 범위를 넘어가지 마세요.

[지시]
{question}

[근거 컨텍스트]
{context}

[출력 형식]
- 한국어로 간결하게 bullet 3개
- 각 bullet 끝에 (출처: 회사 연도 p.페이지) 표기
- 근거에 없으면 "제공된 자료 기준으로 확인되지 않습니다."라고 말하기

답변:"""
)

router = APIRouter(prefix="/rag", tags=["RAG"])

class QueryReq(BaseModel):
    question: str
    top_k: int = 5
    collections: List[str] = ["sr_corpus", "standards"]


def _dedup_docs(docs: List[Document]) -> List[Document]:
    """source + page_from 기준 중복 제거"""
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


# ---- 프롬프트 길이 토큰 기준 컷팅 (Polyglot 3.8B: 컨텍스트 ~2048 권장) ----
from transformers import AutoTokenizer as _AutoTokForLen
_tok4len = None
def _get_len_tokenizer():
    global _tok4len
    if _tok4len is None:
        _tok4len = _AutoTokForLen.from_pretrained(BASE_MODEL)
    return _tok4len

MAX_CTX = 2048
RESERVED = 256  # 생성 여유
def fit_prompt(tokenizer, text, max_len=MAX_CTX-RESERVED):
    ids = tokenizer(text, return_tensors="pt").input_ids[0]
    if len(ids) <= max_len:
        return text
    keep_ids = ids[-max_len:]  # 뒤쪽 유지
    return tokenizer.decode(keep_ids, skip_special_tokens=True)


@router.post("/query")
def query(req: QueryReq):
    # 1) 컬렉션 경로 확인
    paths = []
    for c in req.collections:
        p = collection_path(c)
        if not ((p / "index.faiss").exists() and (p / "index.pkl").exists()):
            raise HTTPException(404, f"FAISS 인덱스가 없습니다: {p}")
        paths.append(p)

    # 2) 컬렉션별 검색 (분배 후 부족분 보충)
    k = max(1, req.top_k)
    per = max(1, k // len(paths))
    docs: List[Document] = []
    for p in paths:
        r = retriever(p, k=per)
        docs.extend(r.invoke(req.question))  # LangChain 최신 권장

    docs = _dedup_docs(docs)

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

    # 3) 컨텍스트 구성
    def fmt(d: Document):
        m = d.metadata or {}
        src = f"{m.get('company','?')} {m.get('year','?')} p.{m.get('page_from','?')}"
        return f"[{src}] {d.page_content.strip()}"
    context = "\n\n".join(fmt(d) for d in docs)

    # 4) 프롬프트 생성 + 길이 컷
    llm = get_llm()
    prompt = PROMPT.format(question=req.question, context=context)
    prompt = fit_prompt(_get_len_tokenizer(), prompt)

    # 5) 생성 (빈 응답 폴백)
    answer = llm.invoke(prompt)
    text = (str(answer) or "").strip()
    if not text:
        text = "제공된 자료 기준으로 확인되는 항목이 없습니다. 질문을 더 구체화하거나 top_k를 늘려보세요."

    # 6) 참고 메타
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

    return {"answer": text, "refs": refs}
