from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Set, Tuple
from pathlib import Path
import os, re
from langchain.prompts import PromptTemplate
from langchain.schema import Document

from .config import LLM_BACKEND, BASE_MODEL, OPENAI_API_KEY
from .vectorstore import retriever, collection_path
from .utils.jsonl_logger import JsonlLogger

_LLM = None

def get_llm():
    """
    HF 로컬(예: Polyglot 3.8B) 또는 OpenAI 백엔드.
    윈도우 환경 안정화를 위해 device_map 미사용, 단일 GPU로 지정.
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

    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from langchain_community.llms import HuggingFacePipeline

    try:
        torch.set_float32_matmul_precision("high")
        if torch.cuda.is_available():
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
    except Exception:
        pass

    tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    if tok.pad_token is None and tok.eos_token is not None:
        tok.pad_token = tok.eos_token

    device = 0 if torch.cuda.is_available() else -1

    mdl = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype="auto",
    )
    if device >= 0:
        mdl = mdl.to("cuda")

    gen = pipeline(
        "text-generation",
        model=mdl,
        tokenizer=tok,
        max_new_tokens=256,
        min_new_tokens=32,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.05,
        return_full_text=False,
        pad_token_id=tok.eos_token_id,
        device=device,
    )

    _LLM = HuggingFacePipeline(pipeline=gen)
    return _LLM


# ------ Prompt ------

PROMPT = PromptTemplate.from_template(
    """다음은 한국어 지시와 참고 소스 목록(SOURCES)입니다.
SOURCES 안의 번호만을 인용 근거로 사용할 수 있습니다.

[지시]
{question}

[SOURCES]
{sources}  # 예: [1] 회사 연도 p.10-12: (요약/발췌)

[작성 규칙]
- 답변은 반드시 아래 4개 섹션 헤더로 구성:
  1) 거버넌스
  2) 전략
  3) 리스크 관리
  4) 지표 및 목표
- 각 섹션은 **3~6개의 bullet**로만 작성
- 각 bullet 끝은 반드시 인용 태그 **[번호]** 로 마무리 (예: …[1])
- bullet에는 가능할 경우 1문장 **직접 인용**(「」로 감싸기) 포함
- **SOURCES에 없는 내용은 절대 추론/가정 금지**
- 답변 본문에 URL/파일명 등 메타데이터 노출 금지
- 근거가 충분치 않은 섹션은 작성하지 말고 해당 섹션에 **INSUFFICIENT_EVIDENCE** 만 기재
- 최종 출력은 반드시 아래 형식을 따라야 함:

# TCFD 보고서 초안
1) 거버넌스
- …[1]
- …[2]

2) 전략
- …[3]

3) 리스크 관리
- …[4]

4) 지표 및 목표
- …[5]
"""
)


router = APIRouter(prefix="/rag", tags=["RAG"])

class QueryReq(BaseModel):
    question: str
    top_k: int = 5
    # 기본 컬렉션: 환경변수 우선 → 없으면 통일된 기본값 사용
    collections: List[str] = [
        os.getenv("SR_COLLECTION", "sr_corpus"),
        os.getenv("STD_COLLECTION", "standards"),
    ]

_qa_logger = JsonlLogger(
    path=os.getenv("QA_JSONL_PATH", "./data/logs/qa_runs.jsonl"),
    rotate_mb=int(os.getenv("QA_JSONL_ROTATE_MB", "200")),
)

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


# ---- 프롬프트 길이 컷팅 ----
from transformers import AutoTokenizer as _AutoTokForLen
_tok4len = None
def _get_len_tokenizer():
    global _tok4len
    if _tok4len is None:
        _tok4len = _AutoTokForLen.from_pretrained(BASE_MODEL, use_fast=True)
    return _tok4len

MAX_CTX = 2048
RESERVED = 256
def fit_prompt(tokenizer, text, max_len=MAX_CTX-RESERVED):
    ids = tokenizer(text, return_tensors="pt").input_ids[0]
    if len(ids) <= max_len:
        return text
    keep_ids = ids[-max_len:]
    return tokenizer.decode(keep_ids, skip_special_tokens=True)


_CITE_RE = re.compile(r"\[\d+\]")

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
        docs.extend(r.invoke(req.question))
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

    # 3) SOURCES 목록 구성 (번호매김)
    def brief(txt: str, n=160):
        s = (txt or "").strip().replace("\n", " ")
        return (s[:n] + "…") if len(s) > n else s

    src_lines = []
    for i, d in enumerate(docs, start=1):
        m = d.metadata or {}
        tag = f"[{i}] {m.get('company','?')} {m.get('year','?')} p.{m.get('page_from','?')}"
        src_lines.append(f"{tag}: {brief(d.page_content)}")
    sources_block = "\n".join(src_lines) if src_lines else "(no sources)"

    # 4) 프롬프트 생성 + 길이 컷
    llm = get_llm()
    prompt = PROMPT.format(question=req.question, sources=sources_block)
    prompt = fit_prompt(_get_len_tokenizer(), prompt)

    # 5) 생성
    answer = llm.invoke(prompt)
    text = (str(answer) or "").strip()

    # 6) 로깅 품질 가드
    insufficient = "INSUFFICIENT_EVIDENCE" in text.upper()
    has_cite = bool(_CITE_RE.search(text))

    # 참고 메타
    refs: List[Dict] = []
    for idx, d in enumerate(docs, start=1):
        m = d.metadata or {}
        refs.append({
            "idx": idx,
            "source": m.get("source"),
            "company": m.get("company"),
            "year": m.get("year"),
            "page_from": m.get("page_from"),
            "page_to": m.get("page_to"),
            "collection": m.get("collection"),
        })

    # 7) JSONL 로그 (근거 미흡/인용 없음이면 스킵)
    if not insufficient and has_cite:
        try:
            retrieved_chunks = []
            for d in docs:
                m = d.metadata or {}
                snippet = brief(d.page_content, 300)
                retrieved_chunks.append({
                    "source": m.get("source"),
                    "company": m.get("company"),
                    "year": m.get("year"),
                    "page_from": m.get("page_from"),
                    "page_to": m.get("page_to"),
                    "collection": m.get("collection"),
                    "text": snippet,
                })
            _qa_logger.log_qa(
                question=req.question,
                answer=text,
                retrieved_chunks=retrieved_chunks,
                citations=refs,
                meta={"route": "/rag/query", "top_k": req.top_k, "collections": req.collections},
            )
        except Exception:
            pass

    # 8) 사용자 응답 (근거 부족 시 안내)
    if insufficient or not has_cite:
        return {
            "answer": "제공된 컨텍스트로 답을 확정하기 어렵습니다. 질문을 더 구체화하거나, top_k를 늘리거나, 관련 문서 범위를 확장해 주세요.",
            "refs": refs
        }
    return {"answer": text, "refs": refs}
