from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path

from langchain.prompts import PromptTemplate
from langchain.schema import Document

from .config import FAISS_DIR, SR_COLLECTION, STD_COLLECTION, LLM_BACKEND, BASE_MODEL, OPENAI_API_KEY
from .vectorstore import retriever
from .embeddings import embeddings

# ---- LLM 선택 (HF 기본, 필요시 OpenAI) ----
def build_llm():
    if LLM_BACKEND == "openai":
        from langchain_openai import ChatOpenAI
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY 미설정")
        return ChatOpenAI(model="gpt-4o-mini", temperature=0)
    else:
        # HF Transformers 파이프라인
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        tok = AutoTokenizer.from_pretrained(BASE_MODEL)
        mdl = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype="auto", device_map="auto")
        gen = pipeline("text-generation", model=mdl, tokenizer=tok, max_new_tokens=512, do_sample=False)
        # LangChain 래핑
        from langchain.llms import HuggingFacePipeline
        return HuggingFacePipeline(pipeline=gen)

LLM = build_llm()

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
    collections: List[str] = ["sr_corpus", "standards"]  # 검색할 코퍼스 선택

@router.post("/query")
def query(req: QueryReq):
    # 1) retriever 묶기
    paths = []
    for c in req.collections:
        p = FAISS_DIR / c
        if not (p / "index.faiss").exists():
            raise HTTPException(404, f"FAISS 인덱스가 없습니다: {p}")
        paths.append(p)

    # 단순 합치기: 각 컬렉션 k//len(paths)씩 가져온 후 합산
    per = max(1, req.top_k // len(paths))
    docs: List[Document] = []
    for p in paths:
        r = retriever(p, k=per)
        docs.extend(r.get_relevant_documents(req.question))

    # 부족하면 첫 컬렉션에서 보충
    if len(docs) < req.top_k:
        r0 = retriever(paths[0], k=req.top_k)
        docs = r0.get_relevant_documents(req.question)

    # 2) 컨텍스트 구성
    def fmt(d: Document):
        m = d.metadata or {}
        src = f"{m.get('company','?')} {m.get('year','?')} p.{m.get('page_from','?')}"
        return f"[{src}] {d.page_content.strip()}"
    context = "\n\n".join(fmt(d) for d in docs[:req.top_k])

    # 3) 생성
    prompt = PROMPT.format(question=req.question, context=context)
    answer = LLM(prompt)

    # 4) 참고 메타 반환
    refs: List[Dict] = []
    for d in docs[:req.top_k]:
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
