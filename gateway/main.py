import sys
import os

# Python 경로에 app 디렉토리 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(
    title="MSA Gateway",
    description="마이크로서비스 아키텍처 Gateway",
    version="1.0.0"
)

# CORS 설정
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
        "message": "MSA Gateway is running!",
        "timestamp": time.time(),
        "status": "healthy",
        "services": ["user-service", "order-service", "product-service"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "gateway",
        "timestamp": time.time()
    }

@app.get("/services")
async def list_services():
    return {
        "services": [
            {
                "name": "user-service",
                "instances": 2,
                "status": "healthy"
            },
            {
                "name": "order-service", 
                "instances": 2,
                "status": "healthy"
            },
            {
                "name": "product-service",
                "instances": 1,
                "status": "healthy"
            }
        ]
    }

@app.get("/docs")
async def docs():
    return {"message": "Swagger docs available at /docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 