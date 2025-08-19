# serve_draft.py
# LangChain으로 RAG 체인 구성: retriever + prompt + HF pipeline(LoRA)
import os
from typing import Dict, Any
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms import HuggingFacePipeline
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel

# 1) 임베딩(검색) 설정: E5는 query에 "query: " 프리픽스!
emb = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base",
    model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

# 기존 인덱스 로드
sr_vs = Chroma(
    collection_name="sr_corpus",
    embedding_function=emb,
    persist_directory=r"C:\taezero\auto_sr\service\tcfdreport-service\chroma_db\sr_corpus"
)
std_vs = Chroma(
    collection_name="standards",
    embedding_function=emb,
    persist_directory=r"C:\taezero\auto_sr\service\tcfdreport-service\chroma_db\standards"
)

# 검색기 (MMR + 필터 예시)
def build_retriever(vs, k=5, fetch_k=20, lambda_mult=0.5, filters: Dict[str, Any] | None = None):
    return vs.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k, "lambda_mult": lambda_mult, "filter": filters or {}}
    )

# 2) LLM: base + LoRA 어댑터 또는 병합본
#  - 어댑터 방식: base를 로드 후 PeftModel.attach
#  - 병합본: repo id 하나만 로드
import torch
BASE_MODEL = "kakaobrain/polyglot-ko-3.8b"  # 예시(5.8B도 가능)
LORA_DIR  = r"C:\taezero\auto_sr\service\tcfdreport-service\outputs\polyglot-3p8b-lora"  # 네가 학습한 경로

tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
if tok.pad_token is None:
    tok.pad_token = tok.eos_token

base = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
llm = PeftModel.from_pretrained(base, LORA_DIR)
gen = pipeline(
    "text-generation",
    model=llm,
    tokenizer=tok,
    device=0 if torch.cuda.is_available() else -1,
    max_new_tokens=512,
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
)
hf_llm = HuggingFacePipeline(pipeline=gen)

# 3) 프롬프트
prompt = ChatPromptTemplate.from_template(
    """다음 요구사항에 맞춰 TCFD 보고서 초안 문장을 한국어로 작성하라.
- 스타일: 객관적, 수동형 최소화, 회사명/연도 일관, 과장 금지
- 숫자/지표는 추론 금지: 근거에 있는 값만 사용
- TCFD 항목: {tcfd_item}
- 회사: {company} / 연도: {year}
- 사용자 입력값:
{user_values}

[표준 근거]
{std_context}

[동종사 SR 근거]
{sr_context}

요구사항을 충족하는 1~2개 문단을 작성하되, 문장 끝에 (근거: {cite_keys}) 형식으로 간단히 출처를 병기하라."""
)

# 4) 체인 구성: (retrieval → prompt → llm → parse)
def join_docs(docs):
    # 간단 포맷: "회사-연도 p.페이지: 내용"
    lines, keys = [], []
    for d in docs:
        meta = d.metadata or {}
        key = f"{meta.get('company','?')}-{meta.get('year','?')} p.{meta.get('page_from','?')}"
        keys.append(key)
        lines.append(f"- [{key}] {d.page_content.strip()[:800]}")
    return "\n".join(lines), ", ".join(keys)

sr_ret  = build_retriever(sr_vs, k=4)
std_ret = build_retriever(std_vs, k=3)

def build_chain():
    # 입력 dict → 두 retriever 병렬 실행 → 프롬프트 채우기 → LLM
    gather = RunnableParallel(
        sr=sr_ret,
        std=std_ret,
        passthrough=RunnablePassthrough()
    )
    def format_inputs(x):
        sr_text, sr_keys   = join_docs(x["sr"])
        std_text, std_keys = join_docs(x["std"])
        cite_keys = "; ".join([std_keys, sr_keys]).strip("; ")
        return {
            "tcfd_item": x["passthrough"]["tcfd_item"],
            "company": x["passthrough"]["company"],
            "year": x["passthrough"]["year"],
            "user_values": x["passthrough"]["user_values"],
            "std_context": std_text,
            "sr_context": sr_text,
            "cite_keys": cite_keys
        }
    chain = (
        gather
        | format_inputs
        | prompt
        | hf_llm
        | StrOutputParser()
    )
    return chain

chain = build_chain()

# 5) 실행 예시
if __name__ == "__main__":
    # E5 쿼리 프리픽스 중요!
    user_query = "query: 리스크 관리 체계 및 TCFD 리스크 평가 절차"
    req = {
        "tcfd_item": "Risk Management",
        "company": "현대모비스",
        "year": "2023",
        "user_values": "- 책임부서: ESG위원회\n- 시나리오: 1.5℃, 2℃\n- 빈도: 연 1회 이상",
        # retriever 내부는 입력 텍스트를 그대로 넘겨도 됨(Chroma 래퍼가 쿼리로 사용)
        "input": user_query
    }
    # LangChain retriever는 내부적으로 x 전체를 받지 않으니, 간단히 질의문을 넣고 검색되도록 patch
    # 대부분의 retriever는 입력 문자열을 그대로 사용하므로 아래처럼 호출:
    out = chain.invoke({
        "tcfd_item": req["tcfd_item"],
        "company": req["company"],
        "year": req["year"],
        "user_values": req["user_values"],
        # retriever들에게 전달될 쿼리는 런타임에서 자동으로 현재 input이 사용됨
        "input": req["input"]
    })
    print(out)
