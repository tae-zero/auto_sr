import sys
import os

# Python 경로에 app 디렉토리 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # ✅ 환경변수 PORT 없으면 기본값 8000
    uvicorn.run(app, host="0.0.0.0", port=port)
