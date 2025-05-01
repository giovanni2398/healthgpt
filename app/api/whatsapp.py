import os
import json
from fastapi import APIRouter, Request, Response, HTTPException, status, BackgroundTasks
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.services.whatsapp_service import WhatsAppService
from app.services.chatgpt_service import ChatGPTService
from app.services.calendar_service import CalendarService

load_dotenv()

router = APIRouter()

# Load the Verify Token from environment variables
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# --- Webhook Verification (GET) ---

@router.get("/webhook")
async def verify_webhook(request: Request):
    """ Handles Meta's webhook verification request. """
    print("Received GET /webhook verification request")
    
    # Parse params from the webhook verification request
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == VERIFY_TOKEN:
            # Respond with 200 OK and challenge token from the request
            print(f"WEBHOOK_VERIFIED: Responding with challenge: {challenge}")
            return Response(content=challenge, status_code=status.HTTP_200_OK)
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            print(f"WEBHOOK_VERIFICATION_FAILED: Mode={mode}, Token={token} (Expected: {VERIFY_TOKEN})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Verify token mismatch",
            )
    else:
        # Responds with '400 Bad Request' if mode or token is missing
        print("WEBHOOK_VERIFICATION_FAILED: Mode or token missing")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing hub.mode or hub.verify_token",
        )

# --- Handle Incoming Messages (POST) ---

async def process_whatsapp_message(payload: dict):
    """
    Processa mensagens recebidas do WhatsApp e orquestra a resposta com ChatGPT e Google Calendar.
    """
    print(f"Processing payload: {json.dumps(payload, indent=2)}")
    
    # Inicializar serviços
    whatsapp_service = WhatsAppService()
    chatgpt_service = ChatGPTService()
    calendar_service = CalendarService()

    # --- 1. Extrair informações relevantes da mensagem --- 
    try:
        # Verificar se é uma mensagem do WhatsApp
        if payload.get('object') == 'whatsapp_business_account':
            entry = payload.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            message_data = value.get('messages', [{}])[0]
            
            if message_data:
                phone_number = message_data.get('from')
                message_type = message_data.get('type')
                
                if message_type == 'text':
                    message_text = message_data.get('text', {}).get('body')
                else:
                    # Ignorar outros tipos de mensagem por enquanto
                    print(f"Ignoring non-text message type: {message_type}")
                    return
                
                if not phone_number or not message_text:
                    print("Could not extract phone number or message text from payload.")
                    return
                    
            else:
                print("No message data found in payload.")
                return
        else:
            # Não é uma notificação do WhatsApp
            print("Ignoring non-whatsapp notification.")
            return
            
    except (IndexError, KeyError, TypeError) as e:
        print(f"Error parsing incoming payload: {e}. Payload: {payload}")
        return

    # --- 2. Processar a mensagem com o ChatGPT ---
    try:
        # Sistema para guiar a resposta do ChatGPT
        system_message = """
        Você é um assistente de agendamento para uma clínica de nutrição. Sua função é:
        1. Entender se o paciente deseja agendar uma consulta
        2. Se sim, identificar possíveis datas/horários mencionados
        3. Responder de forma amigável e profissional
        
        Se o paciente mencionar uma data específica, indique no seu retorno com o formato
        DATA_MENCIONADA: YYYY-MM-DD para que eu possa verificar disponibilidade.
        """
        
        # Gerar resposta com ChatGPT
        response = chatgpt_service.generate_response(message_text, system_message)
        
        # Verificar se ChatGPT identificou uma data
        if "DATA_MENCIONADA:" in response:
            # Extrair a data
            date_str = response.split("DATA_MENCIONADA:")[1].strip().split()[0]
            
            # Verificar slots disponíveis
            available_slots = calendar_service.get_available_slots(date_str)
            
            if available_slots:
                # Formatar slots disponíveis
                slots_text = "\n".join([f"- {slot['time']}" for slot in available_slots[:5]])
                reply = f"Encontrei os seguintes horários disponíveis para {date_str}:\n\n{slots_text}\n\nDeseja confirmar algum destes horários?"
            else:
                reply = f"Infelizmente não temos horários disponíveis para {date_str}. Poderia sugerir outra data?"
        else:
            # Usar a resposta direta do ChatGPT
            reply = response
        
        # Enviar resposta via WhatsApp
        whatsapp_service.send_message(phone_number, reply)
        
    except Exception as e:
        print(f"Error processing message with ChatGPT: {e}")
        # Enviar mensagem de erro genérica
        whatsapp_service.send_message(
            phone_number, 
            "Desculpe, tive um problema ao processar sua mensagem. Por favor, tente novamente."
        )

@router.post("/webhook")
async def receive_whatsapp_message(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint para receber mensagens do webhook do WhatsApp.
    """
    payload = await request.json()
    
    # Processar a mensagem em background para não bloquear a resposta
    background_tasks.add_task(process_whatsapp_message, payload)
    
    # Responder imediatamente com 200 OK para o webhook
    return {"status": "received"}

class ConfirmationPayload(BaseModel):
    phone_number: str = Field(..., description="Número do telefone do paciente com código do país")
    patient_name: str = Field(..., description="Nome completo do paciente")
    appointment_date: str = Field(..., description="Data da consulta (YYYY-MM-DD)")
    appointment_time: str = Field(..., description="Horário da consulta (HH:MM)")

@router.post("/send-confirmation")
async def send_confirmation_message(payload: ConfirmationPayload):
    """
    Envia mensagem de confirmação de agendamento via WhatsApp.
    """
    try:
        whatsapp_service = WhatsAppService()
        
        # Formatar mensagem de confirmação
        message = (
            f"Olá {payload.patient_name},\n\n"
            f"Sua consulta foi agendada com sucesso para o dia {payload.appointment_date} às {payload.appointment_time}.\n\n"
            f"Por favor, chegue com 15 minutos de antecedência. Caso precise remarcar, entre em contato conosco.\n\n"
            f"Atenciosamente,\nEquipe HealthGPT"
        )
        
        # Enviar mensagem
        success = whatsapp_service.send_message(payload.phone_number, message)
        
        if success:
            return {"status": "success", "message": "Confirmation sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send confirmation")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending confirmation: {str(e)}") 