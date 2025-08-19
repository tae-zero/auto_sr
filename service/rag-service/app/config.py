import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

faiss_dir_env = os.getenv("FAISS_DIR")
if not faiss_dir_env:
    raise RuntimeError("FAISS_DIR 가 .env에 설정되어야 합니다.")
FAISS_DIR = Path(faiss_dir_env)

SR_COLLECTION = os.getenv("SR_COLLECTION", "sr_corpus")
STD_COLLECTION = os.getenv("STD_COLLECTION", "standards")

EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "intfloat/multilingual-e5-base")
EMBED_DEVICE = os.getenv("EMBED_DEVICE", "cuda")
EMBED_BATCH_SIZE = int(os.getenv("EMBED_BATCH_SIZE", "16"))

LLM_BACKEND = os.getenv("LLM_BACKEND", "hf")  # "hf" | "openai"
BASE_MODEL = os.getenv("BASE_MODEL", "EleutherAI/polyglot-ko-3.8b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

QUANTIZE = os.getenv("QUANTIZE", "").lower()  # "8bit" | "4bit" | ""
