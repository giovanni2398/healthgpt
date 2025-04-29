import os
import json
from fastapi import APIRouter, Request, Response, HTTPException, status, BackgroundTasks
from dotenv import load_dotenv

from app.services.whatsapp_service import WhatsAppService
from app.services.conversation_state_service import ConversationStateService
from app.services.scheduling_service import SchedulingService
from app.services.appointment_orchestrator import AppointmentOrchestrator

load_dotenv()

router = APIRouter()

# Load the Verify Token from environment variables
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GOOGLE_SCHEDULES_LINK = os.getenv("GOOGLE_SCHEDULES_LINK", "[Insira seu link do Google Schedules aqui]") # Get link from .env or provide default

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
    Processes the incoming WhatsApp message payload in the background.
    This is where the conversation state machine and logic will reside.
    """
    print(f"Processing payload: {json.dumps(payload, indent=2)}")
    
    # Initialize services
    state_service = ConversationStateService()
    whatsapp_service = WhatsAppService()
    # Instantiate other services as needed within the state handlers
    # We might need ChatGPTService, SchedulingService, AppointmentOrchestrator
    chatgpt_service = None # Lazy load if needed
    scheduling_service = None # Lazy load if needed
    orchestrator_service = None # Lazy load if needed

    # --- 1. Extract relevant information from payload --- 
    # Meta's payload structure is complex. Need to extract message type, text, phone number etc.
    # Example (simplified, adjust based on actual Meta payload structure):
    try:
        # Change detection (only process messages)
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
                elif message_type == 'interactive': # e.g., button clicks
                    # Extract data from interactive messages if you use them
                    message_text = "Interactive Message Received" # Placeholder
                else:
                    # Handle other message types if needed (image, audio, location, etc.)
                    print(f"Ignoring non-text/interactive message type: {message_type}")
                    return
                
                if not phone_number or not message_text:
                    print("Could not extract phone number or message text from payload.")
                    return
                    
            else:
                print("No message data found in payload.")
                return
        else:
            # Not a whatsapp message notification
            print("Ignoring non-whatsapp notification.")
            return
            
    except (IndexError, KeyError, TypeError) as e:
        print(f"Error parsing incoming payload: {e}. Payload: {payload}")
        return

    # --- 2. Get current conversation state --- 
    current_state_info = state_service.get_state(phone_number)
    state = "NEW" if current_state_info is None else current_state_info.get("state")
    context = {} if current_state_info is None else current_state_info.get("context", {})
    
    # --- 3. Check if bot should ignore --- 
    if state in ["COMPLETED", "HUMAN_TAKEOVER"]:
        print(f"Ignoring message from {phone_number}. State: {state}")
        return
        
    # --- 4. Implement State Machine Logic --- 
    # TODO: Build the state machine logic here based on 'state' and 'message_text'
    # This will involve calling ChatGPTService, SchedulingService etc. 
    # and using state_service.save_state(phone_number, new_state, new_context)
    
    new_state = state # Placeholder
    new_context = context # Placeholder
    reply_message = "" # Placeholder
    
    if state == "NEW":
        print(f"Handling NEW contact: {phone_number}")
        # Initial response offering link or chat
        reply_message = (
            f"Olá! Bem-vindo(a) à clínica HealthGPT.\n\n"
            f"Você pode ver meus horários e agendar diretamente aqui: {GOOGLE_SCHEDULES_LINK}\n\n"
            f"Ou, se preferir, podemos fazer o agendamento aqui pelo chat. Como gostaria de prosseguir?"
        )
        new_state = "AWAITING_INITIAL_CHOICE" # Transition to next state
        state_service.save_state(phone_number, new_state, new_context) 
        
    elif state == "AWAITING_INITIAL_CHOICE":
        print(f"Handling AWAITING_INITIAL_CHOICE for {phone_number}. Message: '{message_text}'")
        # TODO: Analyze if user wants link (ignore) or chat (start flow)
        # Simplified: Assume any reply means they want to chat for now
        if "link" in message_text.lower():
             reply_message = f"Ok! Use este link para agendar: {GOOGLE_SCHEDULES_LINK}"
             # Decide if you want to end the bot interaction here
             state_service.save_state(phone_number, "REDIRECTED_TO_LINK", {"link_sent": True})
        else:
            reply_message = "Ok, vamos agendar por aqui. Você prefere atendimento particular ou por convênio?"
            new_state = "AWAITING_TYPE"
            state_service.save_state(phone_number, new_state, new_context)
    
    elif state == "AWAITING_TYPE":
        print(f"Handling AWAITING_TYPE for {phone_number}. Message: '{message_text}'")
        msg_lower = message_text.lower()
        
        # Simple keyword matching for now
        if "particular" in msg_lower or "privado" in msg_lower:
            new_context['is_private'] = True
            # Send predefined info message for private consultations
            # TODO: Define this message properly, maybe load from config or template
            reply_message = (
                "Entendido. O atendimento particular funciona assim: [Explicação sobre consulta particular, valores, etc.]. \n"
                "Um de nossos atendentes entrará em contato para finalizar os detalhes e confirmar seu agendamento."
            )
            new_state = "HUMAN_TAKEOVER" # End bot flow here for private
            state_service.save_state(phone_number, new_state, new_context)
        elif "convênio" in msg_lower or "convenio" in msg_lower or "plano" in msg_lower:
            new_context['is_private'] = False
            reply_message = "Ok, qual o nome do seu convênio/plano de saúde?"
            new_state = "AWAITING_INSURANCE_NAME"
            state_service.save_state(phone_number, new_state, new_context)
        else:
            # Could use ChatGPT here for better understanding, but for now, ask again
            reply_message = "Desculpe, não entendi. O atendimento seria particular ou por convênio?"
            # Keep state as AWAITING_TYPE
            state_service.save_state(phone_number, state, context) # Save context in case something useful was stored
            
    elif state == "AWAITING_INSURANCE_NAME":
        print(f"Handling AWAITING_INSURANCE_NAME for {phone_number}. Message: '{message_text}'")
        potential_insurance_name = message_text # Assume the message is the name for now
        
        if orchestrator_service is None: orchestrator_service = AppointmentOrchestrator()
        
        if orchestrator_service.validate_insurance(potential_insurance_name):
            new_context['insurance_name'] = potential_insurance_name
            # Ask for documents next
            reply_message = (
                f"Perfeito, atendemos {potential_insurance_name}. \n"
                f"Para agilizar, por favor, envie aqui no chat fotos legíveis do seu documento de identidade (frente e verso) e da sua carteirinha do convênio (frente e verso)."
            )
            new_state = "AWAITING_DOCS_INSURANCE"
            state_service.save_state(phone_number, new_state, new_context)
        else:
            accepted_list = ", ".join(orchestrator_service.ACCEPTED_INSURANCES)
            reply_message = (
                f"Desculpe, no momento não estamos atendendo o convênio '{potential_insurance_name}'. \n"
                f"Aceitamos: {accepted_list}. \n"
                f"Gostaria de seguir como particular ou tentar informar outro convênio?"
            )
            # Go back or ask to clarify?
            # Let's go back to AWAITING_TYPE state for simplicity
            new_state = "AWAITING_TYPE"
            state_service.save_state(phone_number, new_state, context) # Reset context slightly?
            
    elif state == "AWAITING_DOCS_INSURANCE":
        # User sent something after being asked for docs. Assume they sent them (as per requirement).
        # Move to asking about slots.
        print(f"Handling AWAITING_DOCS_INSURANCE for {phone_number}. Assuming docs received, asking for slots.")
        # TODO: Implement slot fetching and presentation
        reply_message = "Obrigado! Agora, sobre o agendamento, você tem alguma preferência de dia ou horário para a consulta?"
        new_state = "AWAITING_SLOT_PREFERENCE"
        state_service.save_state(phone_number, new_state, new_context)
        
    elif state == "AWAITING_SLOT_PREFERENCE":
        print(f"Handling AWAITING_SLOT_PREFERENCE for {phone_number}. Message: '{message_text}'")
        # For now, assume any response means they want to see available slots.
        # TODO: Implement more sophisticated understanding of preference (e.g., date/time parsing).
        
        if scheduling_service is None: scheduling_service = SchedulingService()
        
        try:
            available_slots = scheduling_service.get_available_slots()
            
            if not available_slots:
                reply_message = "Desculpe, no momento não há horários disponíveis. Por favor, tente novamente mais tarde ou entre em contato conosco diretamente."
                # Keep state or move to human? Let's keep for now, user might ask again.
                new_state = state # Stay in AWAITING_SLOT_PREFERENCE
                state_service.save_state(phone_number, new_state, context)
            else:
                # Format the slots for display
                # TODO: Improve formatting, maybe add button options if platform supports
                slot_options = []
                for slot in available_slots:
                    # Assuming slot object has 'start_time', 'end_time', 'slot_id'
                    # Let's format start_time for simplicity
                    try:
                        # Attempt to parse and format. Adjust format as needed.
                        from datetime import datetime
                        start_dt = datetime.fromisoformat(slot['start_time'])
                        formatted_time = start_dt.strftime("%d/%m/%Y às %H:%M") # Example: 25/07/2024 às 14:30
                        slot_options.append(f"- {formatted_time} (ID: {slot['slot_id']})") # Include ID for selection
                    except (ValueError, KeyError):
                        slot_options.append(f"- Horário inválido (ID: {slot.get('slot_id', 'N/A')})")
                        
                reply_message = "Aqui estão os próximos horários disponíveis:\n" + "\n".join(slot_options) + "\n\nPor favor, digite o ID do horário que deseja escolher."
                new_state = "AWAITING_SLOT_CHOICE"
                state_service.save_state(phone_number, new_state, new_context)
                
        except Exception as e:
            print(f"Error fetching or formatting slots: {e}")
            reply_message = "Ocorreu um erro ao buscar os horários. Por favor, tente novamente mais tarde."
            # Decide state: back to preference or human takeover?
            new_state = "AWAITING_SLOT_PREFERENCE" # Let them try again
            state_service.save_state(phone_number, new_state, context)
          
    elif state == "AWAITING_SLOT_CHOICE":
        print(f"Handling AWAITING_SLOT_CHOICE for {phone_number}. Message: '{message_text}'")
        chosen_slot_id = message_text.strip() # Assume message is the slot ID
        
        # TODO: Add validation for the format of chosen_slot_id if needed
        
        if scheduling_service is None: scheduling_service = SchedulingService()
        
        try:
            reservation_result = scheduling_service.reserve_slot(chosen_slot_id)
            
            if reservation_result.get("success"): # Assuming reserve_slot returns a dict like {"success": True/False, ...}
                # Slot successfully reserved (logically)
                # TODO: Get the reserved slot details (like formatted time) for the confirmation message
                reserved_time = reservation_result.get("formatted_time", "o horário selecionado") # Placeholder
                
                reply_message = (
                    f"Ótimo! Seu horário para {reserved_time} foi pré-agendado com sucesso.\n"
                    f"Nossa equipe irá verificar os documentos enviados e entrará em contato em breve para confirmar tudo. Obrigado!"
                )
                new_state = "APPOINTMENT_PENDING" # Move to a state indicating pending human review/confirmation
                new_context["reserved_slot_id"] = chosen_slot_id # Store the reserved ID
                state_service.save_state(phone_number, new_state, new_context)
            else:
                # Slot could not be reserved (e.g., already taken, invalid ID)
                error_message = reservation_result.get("error", "Não foi possível reservar este horário. Pode ser que ele tenha sido ocupado ou o ID é inválido.")
                reply_message = f"{error_message} Por favor, escolha outro horário da lista abaixo."
                
                # Re-fetch and display available slots
                available_slots = scheduling_service.get_available_slots()
                if not available_slots:
                    reply_message = "Desculpe, não há mais horários disponíveis no momento. Por favor, entre em contato conosco."
                    new_state = "HUMAN_TAKEOVER" # No slots left, escalate
                    state_service.save_state(phone_number, new_state, context)
                else:
                    slot_options = []
                    for slot in available_slots:
                        try:
                            from datetime import datetime
                            start_dt = datetime.fromisoformat(slot['start_time'])
                            formatted_time = start_dt.strftime("%d/%m/%Y às %H:%M")
                            slot_options.append(f"- {formatted_time} (ID: {slot['slot_id']})")
                        except (ValueError, KeyError):
                             slot_options.append(f"- Horário inválido (ID: {slot.get('slot_id', 'N/A')})")
                              
                    reply_message += "\n\n" + "Aqui estão os horários atualizados:\n" + "\n".join(slot_options) + "\n\nPor favor, digite o ID do horário que deseja escolher."
                    new_state = "AWAITING_SLOT_CHOICE" # Stay in this state, but show list again
                    state_service.save_state(phone_number, new_state, context) # Update context if needed
                    
        except Exception as e:
            print(f"Error reserving slot {chosen_slot_id}: {e}")
            reply_message = "Ocorreu um erro ao tentar reservar seu horário. Por favor, tente novamente ou escolha outro horário da lista."
            # Go back to showing the list
            new_state = "AWAITING_SLOT_PREFERENCE" # Go back to the previous state to re-trigger list fetching
            state_service.save_state(phone_number, new_state, context)
    
    else:
        print(f"Unhandled state '{state}' for {phone_number}")
        # Default reply or escalate?
        reply_message = "Desculpe, não entendi. Um de nossos atendentes entrará em contato."
        state_service.save_state(phone_number, "HUMAN_TAKEOVER", context)
        # TODO: Add notification logic for human takeover
    
    # --- 5. Send Reply (if any) --- 
    if reply_message:
        await whatsapp_service.send_message(phone_number, reply_message)


@router.post("/webhook")
async def receive_whatsapp_message(request: Request, background_tasks: BackgroundTasks):
    """
    Receives incoming messages from Meta WhatsApp API.
    Immediately returns 200 OK to Meta and processes the message in the background.
    """
    payload = await request.json()
    # Using background tasks is crucial to avoid timeouts from Meta
    background_tasks.add_task(process_whatsapp_message, payload)
    print("Received POST /webhook. Added to background tasks.")
    return Response(status_code=status.HTTP_200_OK)
