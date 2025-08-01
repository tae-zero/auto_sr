from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import uuid

app = FastAPI(
    title="Chat Service",
    description="AI 채팅 서비스를 제공하는 마이크로서비스",
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

# 데이터 모델
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    timestamp: str

class ChatHistoryItem(BaseModel):
    id: str
    content: str
    role: str
    timestamp: str

# 메모리 기반 채팅 히스토리 (실제로는 데이터베이스 사용)
chat_history: List[ChatHistoryItem] = []

@app.get("/")
async def root():
    return {"message": "Chat Service is running", "service": "chat-service"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "chat-service",
        "timestamp": time.time()
    }

@app.post("/chat")
async def send_message(chat_message: ChatMessage):
    try:
        # 사용자 메시지 저장
        user_message = ChatHistoryItem(
            id=str(uuid.uuid4()),
            content=chat_message.message,
            role="user",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        chat_history.append(user_message)
        
        # AI 응답 생성 (간단한 데모 응답)
        ai_response = f"안녕하세요! '{chat_message.message}'에 대한 답변입니다. 현재는 데모 모드로 작동하고 있습니다."
        
        # AI 응답 저장
        ai_message = ChatHistoryItem(
            id=str(uuid.uuid4()),
            content=ai_response,
            role="assistant",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        chat_history.append(ai_message)
        
        return ChatResponse(
            message=ai_response,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}")

@app.get("/chat/history")
async def get_chat_history():
    return chat_history

@app.delete("/chat/history")
async def clear_chat_history():
    global chat_history
    chat_history.clear()
    return {"message": "채팅 히스토리가 삭제되었습니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 