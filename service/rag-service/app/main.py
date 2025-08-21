from fastapi import FastAPI
from .query import router as rag_router
from .ingest import router as ingest_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title=os.getenv("SERVICE_NAME", "RAG Service (FAISS + LangChain)"),
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계라면 전체 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "service": os.getenv("SERVICE_NAME", "rag-service")}

app.include_router(rag_router)
app.include_router(ingest_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", os.getenv("PORT", "8002")))
    uvicorn.run(app, host=os.getenv("SERVICE_HOST", "0.0.0.0"), port=port)
