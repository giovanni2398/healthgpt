import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import httpx

from app.services.chatgpt_service import ChatGPTService
from app.services.conversation_state import ConversationState, ConversationManager
from app.services.calendar_service import CalendarService, CalendarEvent

load_dotenv()

# Se futuramente você usar uma biblioteca como httpx para chamar a API real,
# basta trocar o corpo desses métodos.

class WhatsAppService:
    """
    Serviço de WhatsApp que integra o ChatGPT para processamento de mensagens.
    Uses the Meta WhatsApp Cloud API to send messages.
    """

    API_VERSION = "v20.0"
    
    # Lista de convênios aceitos
    ACCEPTED_INSURANCES = [
        "unimed",
        "bradesco",
        "sulamerica",
        "amil",
        "porto seguro",
        "notre dame",
        "intermédica",
        "hapvida",
        "santa casa",
        "cassi"
    ]

    def __init__(self):
        self.token = os.getenv("WHATSAPP_API_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.chatgpt_service = ChatGPTService()
        self.calendar_service = CalendarService()
        self.conversation_manager = ConversationManager()

        # Add debug logging
        print(f"DEBUG: Token loaded: {'Yes' if self.token else 'No'}")
        print(f"DEBUG: Phone Number ID loaded: {'Yes' if self.phone_number_id else 'No'}")
        if self.token:
            print(f"DEBUG: Token first 10 chars: {self.token[:10]}...")

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
        
        # --- Input Validation ---
        if not phone or not text:
            print(f"Error: Missing 'from' ({phone}) or 'text' ({text}) in payload: {payload}")
            # Return an error state or a default message
            error_response = "Desculpe, não consegui processar sua mensagem. Faltam dados essenciais."
            # Attempt to use phone if available for state tracking, else use a placeholder
            error_phone = phone or "unknown_sender"
            return {"phone": error_phone, "text": text or "", "response": error_response, "state": ConversationState.ERROR.value}
        # --- End Input Validation ---
        
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
        
        Se o paciente confirmar o agendamento, indique no seu retorno com o formato
        CONFIRMACAO: sim para que eu possa finalizar o agendamento.
        
        Se o paciente mencionar que deseja agendar por convênio, indique no seu retorno com o formato
        CONVENIO: nome_do_convenio para que eu possa verificar se é aceito.
        
        Se o paciente mencionar que deseja agendar particular, indique no seu retorno com o formato
        PARTICULAR: sim para que eu possa informar os valores.
        """
        
        # Processa a mensagem com ChatGPT
        response = self.chatgpt_service.generate_response(text, system_message)
        
        # Atualiza o estado da conversação com base na resposta
        if "PARTICULAR:" in response:
            self.conversation_manager.update_data(phone, {"insurance": "particular"})
            self.conversation_manager.set_state(phone, ConversationState.WAITING_FOR_DATE)
            current_state = ConversationState.WAITING_FOR_DATE
            response = (
                "Ótimo! Para consultas particulares, nossos valores são:\n"
                "💰 Consulta inicial: R$ 200,00\n"
                "💰 Retorno: R$ 150,00\n"
                "💰 Pacote de 4 consultas: R$ 600,00\n\n"
                "Por favor, me informe qual data você gostaria de agendar."
            )
        
        elif "CONVENIO:" in response:
            insurance_name = response.split("CONVENIO:")[1].strip().lower()
            if insurance_name in self.ACCEPTED_INSURANCES:
                self.conversation_manager.update_data(phone, {"insurance": insurance_name})
                self.conversation_manager.set_state(phone, ConversationState.WAITING_FOR_INSURANCE_DOCS)
                current_state = ConversationState.WAITING_FOR_INSURANCE_DOCS
                response = (
                    "Ótimo! Aceitamos seu convênio. Para prosseguir com o agendamento, "
                    "por favor, envie:\n"
                    "1. Foto da carteirinha do convênio\n"
                    "2. Documento pessoal com foto (RG ou CNH)\n\n"
                    "Após o envio dos documentos, podemos prosseguir com o agendamento."
                )
            else:
                response = (
                    f"Desculpe, não trabalhamos com o convênio {insurance_name}. "
                    "Você gostaria de agendar uma consulta particular? "
                    "Nossos valores são:\n"
                    "💰 Consulta inicial: R$ 200,00\n"
                    "💰 Retorno: R$ 150,00\n"
                    "💰 Pacote de 4 consultas: R$ 600,00"
                )
        
        elif "DATA_MENCIONADA:" in response:
            date_str = response.split("DATA_MENCIONADA:")[1].strip().split()[0]
            if self.conversation_manager.is_valid_date(date_str):
                self.conversation_manager.update_data(phone, {"date": date_str})
                self.conversation_manager.set_state(phone, ConversationState.WAITING_FOR_TIME)
                current_state = ConversationState.WAITING_FOR_TIME
        
        elif "HORARIO_MENCIONADO:" in response:
            time_str = response.split("HORARIO_MENCIONADO:")[1].strip().split()[0]
            if self.conversation_manager.is_valid_time(time_str):
                self.conversation_manager.update_data(phone, {"time": time_str})
                self.conversation_manager.set_state(phone, ConversationState.WAITING_FOR_CONFIRMATION)
                current_state = ConversationState.WAITING_FOR_CONFIRMATION
        
        elif "CONFIRMACAO:" in response:
            # Verifica se temos todos os dados necessários
            conversation_data = self.conversation_manager.get_data(phone)
            date_str = conversation_data.get("date")
            time_str = conversation_data.get("time")
            insurance = conversation_data.get("insurance")
            
            if date_str and time_str:
                # Cria o evento no Google Calendar
                start_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                end_time = start_time + timedelta(hours=1)
                
                # Cria o evento no calendário
                # event_created = self.calendar_service.create_calendar_event(
                #     start_time=start_time,
                #     end_time=end_time,
                #     patient_name="Paciente",  # TODO: Obter nome do paciente
                #     patient_phone=phone,
                #     reason=f"Consulta de Nutrição - {insurance}"
                # )
                
                # Create a CalendarEvent object
                calendar_event_data = CalendarEvent(
                    start_time=start_time,
                    end_time=end_time,
                    patient_name="Paciente", # TODO: Get real name
                    patient_phone=phone, 
                    reason=f"Consulta Nutrição - {insurance or 'Particular'}",
                    insurance=insurance
                )
                
                try:
                    # Call the service with the CalendarEvent object
                    event_id = self.calendar_service.create_calendar_event(calendar_event_data)
                    event_created = bool(event_id) # Consider successful if an ID is returned
                except Exception as e:
                    print(f"Error creating calendar event: {e}")
                    event_created = False
                
                if event_created:
                    # Envia confirmação
                    # Assume we need a template for this
                    # Placeholder: Use send_message for now, needs update later
                    # confirmation_sent = self.send_appointment_confirmation(
                    #     phone=phone,
                    #     patient_name="Paciente",  # TODO: Obter nome do paciente
                    #     appointment_date=start_time,
                    #     reason=f"Consulta de Nutrição - {insurance}"
                    # )
                    # TODO: Implement template sending for confirmation
                    # For now, just update state and response
                    confirmation_sent = True # Assume sent for now
                    
                    # Atualiza o estado
                    self.conversation_manager.set_state(phone, ConversationState.COMPLETED)
                    current_state = ConversationState.COMPLETED
                    response = "✅ Agendamento confirmado com sucesso!"
                else:
                    # Erro ao criar evento
                    self.conversation_manager.set_state(phone, ConversationState.ERROR)
                    current_state = ConversationState.ERROR
                    response = "Desculpe, tive um problema ao criar o agendamento. Por favor, tente novamente."
        
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

        # --- DEBUG --- 
        # print(f"DEBUG: Attempting to send message TO: {phone}, Payload: {payload}")
        # --- END DEBUG ---

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

    def send_template_message(
        self,
        phone: str,
        template_name: str,
        language_code: str = "en_US", # Default to English US
        components: Optional[list] = None # Optional components for templates with variables
    ) -> bool:
        """
        Sends a template message using the Meta WhatsApp Cloud API.

        Args:
            phone: The recipient's phone number (E.164 format recommended).
            template_name: The name of the pre-approved template.
            language_code: The language code of the template (e.g., "en_US", "pt_BR").
            components: Optional list of components for templates with variables.

        Returns:
            True if the API request was successful (status code 200).
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
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }
        # Add components if provided (for templates with variables)
        if components:
            payload["template"]["components"] = components

        try:
            with httpx.Client() as client:
                response = client.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
                print(f"Template message '{template_name}' sent successfully to {phone}. Response: {response.json()}")
                return response.status_code == 200
        except httpx.HTTPStatusError as e:
            print(f"HTTP error sending template message '{template_name}' to {phone}: {e.response.status_code} - {e.response.text}")
            return False
        except httpx.RequestError as e:
            print(f"Request error sending template message '{template_name}' to {phone}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error sending template message '{template_name}' to {phone}: {e}")
            return False

    def send_appointment_confirmation(
        self,
        phone: str,
        patient_name: str,
        appointment_date: datetime,
        reason: str
    ) -> tuple:
        """
        Envia uma mensagem de confirmação de agendamento via WhatsApp usando um template.
        
        Args:
            phone: Número de telefone do paciente (formato E.164 recomendado)
            patient_name: Nome do paciente
            appointment_date: Data e hora do agendamento (objeto datetime)
            reason: Motivo da consulta (não usado diretamente no template, mas pode ser útil para logs ou futuras variações)
            
        Returns:
            tuple: (success_status, components_list)
        """
        # --- Configuração do Template ---
        template_name = "appointment_confirmation_v2" 
        language_code = "pt_BR"
        
        # --- Formatação das Variáveis ---
        try:
            # Formata a data e hora para o template (ex: "13/04/2025 - 08:30")
            formatted_date_time = appointment_date.strftime("%d/%m/%Y - %H:%M")
        except AttributeError:
            print(f"Error formatting appointment date: {appointment_date}")
            formatted_date_time = "Data/Hora inválida"
            return False, []

        # --- Construção dos Componentes (Variáveis) --- 
        components = [
            {
                "type": "body",
                "parameters": [
                    {
                        "type": "text",
                        "parameter_name": "paciente",
                        "text": patient_name
                    },
                    {
                        "type": "text",
                        "parameter_name": "data",
                        "text": formatted_date_time
                    }
                ]
            }
        ]
        
        # --- Envio via Template ---
        print(f"Sending template '{template_name}' to {phone} with components: {components}")
        success = self.send_template_message(
            phone=phone,
            template_name=template_name,
            language_code=language_code,
            components=components
        )
        return success, components

        # --- Código antigo (usando send_message) --- 
        # Formata a data para exibição
        # formatted_date = appointment_date.strftime("%d/%m/%Y às %H:%M")
        # 
        # Cria a mensagem de confirmação
        # message = (
        #     f"✅ Agendamento Confirmado!\n\n"
        #     f"Olá {patient_name},\n\n"
        #     f"Seu agendamento foi confirmado para:\n"
        #     f"📅 Data: {formatted_date}\n"
        #     f"📝 Motivo: {reason}\n\n"
        #     f"Se precisar reagendar ou cancelar, entre em contato conosco.\n"
        #     f"Até breve! 👋"
        # )
        # 
        # Envia a mensagem
        # return self.send_message(phone, message)
