from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from app.router import gri_router
from app.common.database.database import engine
from app.common.models import Base

# 환경변수 로드
if not os.getenv("RAILWAY_ENVIRONMENT"):
    load_dotenv()

app = FastAPI(
    title=os.getenv("SERVICE_NAME", "GRI Report Service"),
    description="GRI 기준 지속가능성 보고서 생성 서비스",
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
app.include_router(gri_router.router, prefix="/api/v1/gri")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": os.getenv("SERVICE_NAME", "gri-report-service")}

@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 데이터베이스 테이블 생성 시도"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ GRI Service 데이터베이스 테이블 생성 완료")
    except Exception as e:
        print(f"⚠️ GRI Service 데이터베이스 테이블 생성 실패 (서비스는 계속 실행): {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", os.getenv("PORT", "8006")))
    uvicorn.run(app, host=os.getenv("SERVICE_HOST", "0.0.0.0"), port=port)
