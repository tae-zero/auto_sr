import os
from pathlib import Path

FAISS_DIR = Path(os.getenv("FAISS_DIR", "./vectordb"))
SR_COLLECTION = os.getenv("SR_COLLECTION", "sr_corpus")
STD_COLLECTION = os.getenv("STD_COLLECTION", "standards")

EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "intfloat/multilingual-e5-base")
EMBED_DEVICE = os.getenv("EMBED_DEVICE", "cuda")
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "16"))

LLM_BACKEND = os.getenv("LLM_BACKEND", "hf")  # "hf" | "openai"
BASE_MODEL = os.getenv("BASE_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
