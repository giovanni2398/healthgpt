import os
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv
import httpx

from app.services.chatgpt_service import ChatGPTService
from app.services.conversation_state import ConversationState, ConversationManager

load_dotenv()

# Se futuramente você usar uma biblioteca como httpx para chamar a API real,
# basta trocar o corpo desses métodos.

class WhatsAppService:
    """
    Serviço de WhatsApp que integra o ChatGPT para processamento de mensagens.
    Uses the Meta WhatsApp Cloud API to send messages.
    """

    API_VERSION = "v19.0"

    def __init__(self):
        self.token = os.getenv("WHATSAPP_API_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.chatgpt_service = ChatGPTService()
        self.conversation_manager = ConversationManager()

        if not self.token or not self.phone_number_id:
            print("Warning: WhatsApp credentials (Token or Phone Number ID) not found in .env")

        self.api_url = f"https://graph.facebook.com/{self.API_VERSION}/{self.phone_number_id}/messages"

    def receive_message(self, payload: Dict) -> Dict:
        """
        Processa uma mensagem recebida pelo webhook.
        'payload' é o JSON enviado pelo provedor (Twilio, 360dialog etc.).
        Aqui, extraímos o telefone e o texto, e processamos com ChatGPT.
        """
        phone = payload.get("from")
        text = payload.get("text")
        
        # Obtém o estado atual da conversação
        current_state = self.conversation_manager.get_state(phone)
        
        # Sistema para guiar a resposta do ChatGPT
        system_message = """
        Você é um assistente de agendamento de uma clínica de nutrição.
        Sua função é ajudar os pacientes a agendarem consultas.
        Seja educado, profissional e direto.
        
        Se o paciente mencionar uma data específica, indique no seu retorno com o formato
        DATA_MENCIONADA: YYYY-MM-DD para que eu possa verificar disponibilidade.
        
        Se o paciente mencionar um horário específico, indique no seu retorno com o formato
        HORARIO_MENCIONADO: HH:MM para que eu possa verificar disponibilidade.
        """
        
        # Processa a mensagem com ChatGPT
        response = self.chatgpt_service.generate_response(text, system_message)
        
        # Atualiza o estado da conversação com base na resposta
        if "DATA_MENCIONADA:" in response:
            date_str = response.split("DATA_MENCIONADA:")[1].strip().split()[0]
            if self.conversation_manager.is_valid_date(date_str):
                self.conversation_manager.update_data(phone, {"date": date_str})
                self.conversation_manager.set_state(phone, ConversationState.WAITING_FOR_TIME)
        
        if "HORARIO_MENCIONADO:" in response:
            time_str = response.split("HORARIO_MENCIONADO:")[1].strip().split()[0]
            if self.conversation_manager.is_valid_time(time_str):
                self.conversation_manager.update_data(phone, {"time": time_str})
                self.conversation_manager.set_state(phone, ConversationState.WAITING_FOR_CONFIRMATION)
        
        return {"phone": phone, "text": text, "response": response, "state": current_state.value}

    def send_message(self, phone: str, message: str) -> bool:
        """
        Sends a message using the Meta WhatsApp Cloud API.
        Returns True if the API request was successful (status code 200).
        """
        if not self.token or not self.phone_number_id:
            print("Error: WhatsApp service not configured.")
            return False

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"body": message}
        }

        try:
            with httpx.Client() as client:
                response = client.post(self.api_url, headers=headers, json=payload)

            response.raise_for_status()
            
            if response.status_code == 200:
                print(f"Message sent successfully to {phone}. Response: {response.json()}")
                return True
            else:
                print(f"Failed to send message to {phone}. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except httpx.RequestError as exc:
            print(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            return False
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False

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
