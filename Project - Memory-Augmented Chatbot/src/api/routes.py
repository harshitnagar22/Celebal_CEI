from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.agent.graph import chat

# router for chat api
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user" # default user if not passed

class ChatResponse(BaseModel):
    response: str
    user_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # pass the query to our langgraph agent
        response_text = chat(request.message, thread_id=request.user_id)
        
        return ChatResponse(
            response=response_text,
            user_id=request.user_id
        )
    except Exception as e:
        # TODO: handle this better later, maybe log it
        print("error in chat:", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "ok"} # just checking if alive
