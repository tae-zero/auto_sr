from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

app = FastAPI(
    title="Simple MSA Gateway",
    description="간단한 API Gateway",
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
        "message": "Simple MSA Gateway is running",
        "timestamp": time.time(),
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
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
                "status": "available",
                "instances": 1
            },
            {
                "name": "order-service", 
                "status": "available",
                "instances": 1
            }
        ]
    }

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_request(service_name: str, path: str, request: Request):
    return {
        "message": f"Proxying request to {service_name}/{path}",
        "method": request.method,
        "service": service_name,
        "path": path,
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 