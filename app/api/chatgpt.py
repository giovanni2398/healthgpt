from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.chatgpt_service import ChatGPTService

router = APIRouter()
service = ChatGPTService()

class ChatRequest(BaseModel):
    user_message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/mock", response_model=ChatResponse)
async def chat_mock(request: ChatRequest):
    """
    Endpoint de mock: recebe JSON { "user_message": "Olá" }
    e retorna { "reply": "Mocked response to: «Olá»..." }
    """
    try:
        reply = service.generate_response(request.user_message)
        return ChatResponse(reply=reply)
    except Exception as e:
        # Tratamento profissional de erro
        raise HTTPException(status_code=500, detail=str(e))
