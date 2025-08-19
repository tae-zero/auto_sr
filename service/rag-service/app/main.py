from fastapi import FastAPI
from .query import router as rag_router
from .ingest import router as ingest_router

app = FastAPI(title="RAG Service (FAISS + LangChain)")

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(rag_router)
app.include_router(ingest_router)
