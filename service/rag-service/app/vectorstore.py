from pathlib import Path
from typing import Literal
from langchain_community.vectorstores import FAISS, DistanceStrategy
from .embeddings import embeddings

def load_faiss_store(path: Path):
    return FAISS.load_local(
        str(path),
        embeddings,
        allow_dangerous_deserialization=True,
        distance_strategy=DistanceStrategy.COSINE,
    )

def retriever(path: Path, k: int = 5):
    store = load_faiss_store(path)
    return store.as_retriever(search_type="similarity", search_kwargs={"k": k})
