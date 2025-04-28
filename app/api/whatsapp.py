from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.whatsapp_service import WhatsAppService

router = APIRouter()
service = WhatsAppService()

# Modelos Pydantic para validar entrada/saída de dados
class IncomingMessage(BaseModel):
    from_: str  # número do remetente
    text: str

    class Config:
        fields = {'from_': 'from'}  # mapeia o campo JSON "from" para atributo from_

class OutgoingMessage(BaseModel):
    success: bool
    detail: str
    to: str

@router.post("/webhook", response_model=OutgoingMessage)
async def whatsapp_webhook(msg: IncomingMessage):
    """
    Endpoint que seria chamado pelo provedor de WhatsApp (webhook).
    Recebe JSON:
      { "from": "+5511999999999", "text": "Olá" }
    Retorna:
      { "success": true, "detail": "...", "to": "+5511999999999" }
    """
    try:
        # Processa a mensagem recebida
        incoming = {"from": msg.from_, "text": msg.text}
        data = await service.receive_message(incoming)

        # Envia a resposta gerada pelo ChatGPT
        sent = service.send_message(data['phone'], data['response'])

        if not sent:
            raise RuntimeError("Falha no envio da mensagem")

        return OutgoingMessage(success=True, detail="Mensagem enviada com sucesso", to=data["phone"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
