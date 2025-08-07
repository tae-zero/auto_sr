from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Chatbot Service", version="1.0.0")

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
    return {"message": "Chatbot Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatbot-service"}

@app.get("/chat")
async def chat():
    return {"message": "Chat endpoint"}
