import os
from typing import Dict
from datetime import datetime

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
        Retorna True se "enviado com sucesso".
        """
        print(f"[MOCK] Enviar para {phone}: {message}")
        # Aqui você usaria httpx.post(..., headers={'Authorization': self.token}, json={...})
        return True

    def send_appointment_confirmation(
        self,
        phone: str,
        patient_name: str,
        appointment_date: datetime,
        reason: str
    ) -> bool:
        """
        Envia uma mensagem de confirmação de agendamento.
        
        Args:
            phone: Número de telefone do paciente
            patient_name: Nome do paciente
            appointment_date: Data e hora do agendamento
            reason: Motivo da consulta
            
        Returns:
            bool: True se a mensagem foi enviada com sucesso
        """
        # Formata a data para exibição
        formatted_date = appointment_date.strftime("%d/%m/%Y às %H:%M")
        
        # Cria a mensagem de confirmação
        message = (
            f"✅ Agendamento Confirmado!\n\n"
            f"Olá {patient_name},\n\n"
            f"Seu agendamento foi confirmado para:\n"
            f"📅 Data: {formatted_date}\n"
            f"📝 Motivo: {reason}\n\n"
            f"Se precisar reagendar ou cancelar, entre em contato conosco.\n"
            f"Até breve! 👋"
        )
        
        # Envia a mensagem
        return self.send_message(phone, message)
