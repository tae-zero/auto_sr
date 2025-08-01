import sys
import os

# Python 경로에 app 디렉토리 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.main import app
except ImportError as e:
    print(f"Import error: {e}")
    # 간단한 fallback app 생성
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import time
    
    app = FastAPI(
        title="Gateway Fallback",
        description="Gateway fallback due to import error",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Gateway fallback is running",
            "error": "Main gateway import failed",
            "timestamp": time.time()
        }
    
    @app.get("/health")
    async def health():
        return {"status": "fallback", "service": "gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 