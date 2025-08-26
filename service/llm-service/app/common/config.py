import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# 🚀 서비스 설정
# =============================================================================
SERVICE_NAME = os.getenv("SERVICE_NAME", "llm-service")
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("PORT", "8000"))  # Docker Compose(8009) 및 Railway에서 자동으로 PORT 환경변수 제공

# =============================================================================
# 📁 FAISS Volume 설정 (vectordb 구조)
# =============================================================================
FAISS_VOLUME_PATH = os.getenv("FAISS_VOLUME_PATH", "./vectordb")
FAISS_INDEX_NAME = os.getenv("FAISS_INDEX_NAME", "sr_corpus")
FAISS_STORE_NAME = os.getenv("FAISS_STORE_NAME", "sr_corpus")

# FAISS 파일 경로 (지속가능경영보고서)
FAISS_INDEX_PATH = Path(FAISS_VOLUME_PATH) / FAISS_INDEX_NAME / "index.faiss"
FAISS_STORE_PATH = Path(FAISS_VOLUME_PATH) / FAISS_STORE_NAME / "index.pkl"

# TCFD 기준서 FAISS 파일 경로 (추가)
TCFD_INDEX_PATH = Path(FAISS_VOLUME_PATH) / "standards" / "index.faiss"
TCFD_STORE_PATH = Path(FAISS_VOLUME_PATH) / "standards" / "index.pkl"

# =============================================================================
# 🔤 임베딩 모델 설정 (이미 임베딩된 FAISS 사용)
# =============================================================================
# 기존 FAISS 인덱스의 차원 (차원 일치 검증용)
EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))
# OpenAI API 키 (텍스트 생성용만)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# =============================================================================
# 🤖 생성 모델 설정
# =============================================================================
# OpenAI 설정
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# 외부 GPU(vLLM/TGI) KoAlpaca 설정
GENAI_URL = os.getenv("GENAI_URL", "")
GENAI_KEY = os.getenv("GENAI_KEY", "")

# Hugging Face 설정
HF_API_URL = os.getenv("HF_API_URL", "https://api-inference.huggingface.co")
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")  # 빈 문자열이면 fallback 모드로 동작
HF_MODEL = os.getenv("HF_MODEL", "EleutherAI/polyglot-ko-3.8b")
HF_TIMEOUT = int(os.getenv("HF_TIMEOUT", "30"))

# =============================================================================
# 🔒 보안 설정
# =============================================================================
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "supersecret")

# =============================================================================
# 📊 모니터링 설정
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "true").lower() == "true"

# =============================================================================
# 🔧 유틸리티 설정
# =============================================================================
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "20971520"))  # 20MB
SUPPORTED_FILE_TYPES = os.getenv("SUPPORTED_FILE_TYPES", "txt,pdf,docx,md").split(",")

# 기본 top_k 값
DEFAULT_TOP_K = 5
MAX_TOP_K = 20
