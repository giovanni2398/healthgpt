from fastapi import APIRouter

router = APIRouter()

@router.post("/receive")
async def receive_message():
    return {"message": "Mensagem recebida do WhatsApp"}