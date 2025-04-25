import os
from typing import Dict

from dotenv import load_dotenv

load_dotenv()

# Se futuramente você usar uma biblioteca como httpx para chamar a API real,
# basta trocar o corpo desses métodos.

class WhatsAppService:
    """
    Mock de serviço de WhatsApp. Em produção, você trocaria
    o método send_message por uma chamada à API (ex: Twilio, 360dialog).
    """

    def __init__(self):
        # Exemplo de token no .env: WHATSAPP_API_TOKEN
        self.token = os.getenv("WHATSAPP_API_TOKEN")

    def receive_message(self, payload: Dict) -> Dict:
        """
        Simula o processamento de uma mensagem recebida pelo webhook.
        'payload' é o JSON enviado pelo provedor (Twilio, 360dialog etc.).
        Aqui, extraímos só o telefone e o texto.
        """
        # Exemplo de payload:
        # { "from": "+5511999999999", "text": "Olá, quero agendar" }
        phone = payload.get("from")
        text = payload.get("text")
        # Mock de lógica: sempre responde com eco
        return {"phone": phone, "text": text}

    def send_message(self, phone: str, message: str) -> bool:
        """
        Simula o envio de mensagem. Em prod, faria POST na API.
        Retorna True se “enviado com sucesso”.
        """
        print(f"[MOCK] Enviar para {phone}: {message}")
        # Aqui você usaria httpx.post(..., headers={'Authorization': self.token}, json={...})
        return True
