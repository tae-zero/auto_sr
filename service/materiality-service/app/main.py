from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.router import materiality_router
from app.common.database.database import engine
from app.common.models import Base

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Materiality Service",
    description="Materiality 분석 서비스",
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

# 라우터 등록
app.include_router(materiality_router.router, prefix="/api/v1/materiality")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "materiality-service"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8007))
    uvicorn.run(app, host="0.0.0.0", port=port)
