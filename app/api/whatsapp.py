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
        # Processa a mensagem recebida (mock)
        incoming = {"from": msg.from_, "text": msg.text}
        data = service.receive_message(incoming)

        # Exemplo de resposta automática (aqui, ecoamos o texto)
        reply_text = f"Você disse: {data['text']}"

        # Mock de envio
        sent = service.send_message(data['phone'], reply_text)

        if not sent:
            raise RuntimeError("Falha no envio da mensagem")

        return OutgoingMessage(success=True, detail="Mensagem enviada (mock)", to=data["phone"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
