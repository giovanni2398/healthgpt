import os
import json
from fastapi import APIRouter, Request, Response, HTTPException, status, BackgroundTasks
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.services.whatsapp_service import WhatsAppService
from app.services.conversation_state_service import ConversationStateService
from app.services.scheduling_service import SchedulingService
from app.services.appointment_orchestrator import AppointmentOrchestrator
from app.services.chatgpt_service import ChatGPTService

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
            # Ask for Name next
            reply_message = f"Perfeito, atendemos {potential_insurance_name}. Qual o seu nome completo, por favor?"
            new_state = "AWAITING_NAME" # Go to collect name
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
            
    elif state == "AWAITING_NAME":
        print(f"Handling AWAITING_NAME for {phone_number}. Message: '{message_text}'")
        patient_name = message_text.strip()
        # TODO: Add basic validation for name? (e.g., length, format)
        new_context['patient_name'] = patient_name
        reply_message = f"Obrigado, {patient_name.split()[0]}. Agora, por favor, informe sua data de nascimento (DD/MM/AAAA)."
        new_state = "AWAITING_DOB"
        state_service.save_state(phone_number, new_state, new_context)

    elif state == "AWAITING_DOB":
        print(f"Handling AWAITING_DOB for {phone_number}. Message: '{message_text}'")
        dob_text = message_text.strip()
        # TODO: Add validation for date format (DD/MM/AAAA)
        # TODO: Potentially convert to standard date format here?
        new_context['dob'] = dob_text
        # Now ask for documents
        reply_message = (
             f"Entendido. Para finalizar a verificação do convênio \"{new_context.get('insurance_name', '')}\", "
             f"por favor, envie aqui no chat fotos legíveis do seu documento de identidade (frente e verso) "
             f"e da sua carteirinha do convênio (frente e verso)."
        )
        new_state = "AWAITING_DOCS_INSURANCE"
        state_service.save_state(phone_number, new_state, new_context)

    elif state == "AWAITING_DOCS_INSURANCE":
        # Move to asking about slots.
        print(f"Handling AWAITING_DOCS_INSURANCE for {phone_number}. Assuming docs received, asking for slots.")
        # TODO: Implement slot fetching and presentation
        reply_message = "Obrigado! Agora, sobre o agendamento, você tem alguma preferência de dia ou horário para a consulta?"
        new_state = "AWAITING_SLOT_PREFERENCE"
        state_service.save_state(phone_number, new_state, new_context)
        
    elif state == "AWAITING_SLOT_PREFERENCE":
        print(f"Handling AWAITING_SLOT_PREFERENCE for {phone_number}. Message: '{message_text}'")
        
        if scheduling_service is None: scheduling_service = SchedulingService()
        if chatgpt_service is None: 
            chatgpt_service = ChatGPTService()
        
        try:
            available_slots_all = scheduling_service.get_available_slots()
            
            if not available_slots_all:
                reply_message = "Desculpe, no momento não há horários disponíveis. Por favor, tente novamente mais tarde ou entre em contato conosco diretamente."
                # Keep state or move to human? Let's keep for now, user might ask again.
                new_state = state # Stay in AWAITING_SLOT_PREFERENCE
                state_service.save_state(phone_number, new_state, context)
            else:
                # Use ChatGPT to filter slots based on user preference
                print("Attempting to filter slots with ChatGPT...")
                try:
                   filtered_slots = chatgpt_service.filter_slots_by_preference(
                        user_message=message_text,
                        available_slots=available_slots_all
                   )
                   print(f"ChatGPT filtering returned {len(filtered_slots)} slots.")
                except Exception as chat_err:
                   print(f"Error during ChatGPT slot filtering: {chat_err}. Falling back to all slots.")
                   filtered_slots = available_slots_all # Fallback
                   
                if not filtered_slots:
                   # Either no slots matched the preference, or filtering failed and there were no slots initially
                   reply_message = "Desculpe, não encontrei horários disponíveis que correspondam à sua preferência. Gostaria de ver todos os horários disponíveis?"
                   new_state = "AWAITING_SLOT_PREFERENCE_ALL" # New state to handle showing all after filtering failed
                   state_service.save_state(phone_number, new_state, context) # Save context in case preference is useful
                   # Avoid sending empty list below
                   available_slots = [] 
                else:
                   available_slots = filtered_slots
               
                # Format the slots for display
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
                        
                # Only proceed if we actually have slots to show after filtering
                if available_slots: 
                    reply_message = "Encontrei estes horários que correspondem à sua preferência:\n" + "\n".join(slot_options) + "\n\nPor favor, digite o ID do horário que deseja escolher."
                    new_state = "AWAITING_SLOT_CHOICE"
                    state_service.save_state(phone_number, new_state, new_context)
                # Else: The 'no slots found matching preference' message was set above, and state is AWAITING_SLOT_PREFERENCE_ALL
                
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
                
                # --- Attempt to create Google Calendar event --- 
                print(f"Slot {chosen_slot_id} reserved internally. Attempting GCal event creation.")
                if scheduling_service is None: scheduling_service = SchedulingService() # Ensure service is available
                
                # 1. Gather necessary info
                patient_name = new_context.get("patient_name", "Nome não encontrado")
                dob = new_context.get("dob", "Data Nasc. não encontrada")
                insurance_name = new_context.get("insurance_name", "Particular")
                # reservation_result likely contains slot details like start/end times needed by GCal
                slot_details = reservation_result.get("slot_data", {}) # Assuming reserve_slot returns full slot data
                start_time = slot_details.get("start_time")
                end_time = slot_details.get("end_time")

                if not start_time or not end_time:
                    print(f"ERROR: Missing start/end time from reservation_result for slot {chosen_slot_id}. Cannot create GCal event.")
                    # Handle error - maybe escalate to human? Free the slot.
                    reply_message = "Desculpe, ocorreu um erro interno ao processar os detalhes do horário. Nossa equipe entrará em contato."
                    try: scheduling_service.free_slot(chosen_slot_id) # Placeholder for freeing slot
                    except AttributeError: print("Placeholder: scheduling_service.free_slot not implemented")
                    except Exception as free_err: print(f"Error freeing slot {chosen_slot_id}: {free_err}")
                    new_state = "HUMAN_TAKEOVER"
                    state_service.save_state(phone_number, new_state, context)
                else:
                    patient_info = {
                        "name": patient_name,
                        "dob": dob, # Date of Birth
                        "phone": phone_number, # User's WhatsApp number
                        "insurance": insurance_name
                    }
                    
                    # 2. Call placeholder function to create event
                    try:
                        # TODO: Replace placeholder with actual call to Calendar service
                        # calendar_service = CalendarService()
                        # event_created = await calendar_service.create_event(start_time, end_time, patient_info)
                        print(f"Placeholder: Calling create_calendar_event for {patient_name} at {start_time}")
                        # Simulate success/failure for now
                        event_created = True # Assume success for now

                        if event_created:
                            # 3a. Event created successfully - Send final confirmation
                            print(f"GCal event created successfully for slot {chosen_slot_id}.")
                            # Format confirmation message using collected data
                            from datetime import datetime
                            try:
                                dt_obj = datetime.fromisoformat(start_time)
                                appointment_details_str = dt_obj.strftime("%d/%m/%Y às %H:%M")
                            except ValueError:
                                appointment_details_str = "o horário selecionado"
                                
                            reply_message = (
                                f"Agendamento confirmado! ✅\n\n"
                                f"Olá {patient_name}, seu agendamento para {appointment_details_str} foi confirmado com sucesso. "
                                f"Aguardamos você!"
                            )
                            new_state = "COMPLETED" # Final state
                            # Keep context or clear it?
                            state_service.save_state(phone_number, new_state, new_context) 
                        else:
                            # 3b. Event creation failed
                            print(f"GCal event creation FAILED for slot {chosen_slot_id}.")
                            reply_message = "Consegui reservar seu horário, mas ocorreu um problema ao registrar o agendamento na nossa agenda. Nossa equipe revisará e entrará em contato para confirmar, ok?"
                            # Free the slot that was reserved internally
                            try: scheduling_service.free_slot(chosen_slot_id) # Placeholder for freeing slot
                            except AttributeError: print("Placeholder: scheduling_service.free_slot not implemented")
                            except Exception as free_err: print(f"Error freeing slot {chosen_slot_id}: {free_err}")
                            new_state = "HUMAN_TAKEOVER"
                            state_service.save_state(phone_number, new_state, context) # Keep context for human

                    except Exception as cal_err:
                        # Handle exceptions during the calendar creation attempt
                        print(f"ERROR during calendar event creation attempt for slot {chosen_slot_id}: {cal_err}")
                        reply_message = "Desculpe, ocorreu um erro inesperado ao tentar confirmar seu agendamento na agenda. Nossa equipe entrará em contato."
                        # Free the slot
                        try: scheduling_service.free_slot(chosen_slot_id) # Placeholder
                        except AttributeError: print("Placeholder: scheduling_service.free_slot not implemented")
                        except Exception as free_err: print(f"Error freeing slot {chosen_slot_id}: {free_err}")
                        new_state = "HUMAN_TAKEOVER"
                        state_service.save_state(phone_number, new_state, context)

       except Exception as e:
            print(f"Error reserving slot {chosen_slot_id}: {e}")
            reply_message = "Ocorreu um erro ao tentar reservar seu horário. Por favor, tente novamente ou escolha outro horário da lista."
            # Go back to showing the list
            new_state = "AWAITING_SLOT_PREFERENCE" # Go back to the previous state to re-trigger list fetching
            state_service.save_state(phone_number, new_state, context)
    
    elif state == "AWAITING_SLOT_PREFERENCE_ALL":
        print(f"Handling AWAITING_SLOT_PREFERENCE_ALL for {phone_number}. User wants to see all slots.")

        if scheduling_service is None: scheduling_service = SchedulingService()

        try:
            available_slots_all = scheduling_service.get_available_slots()

            if not available_slots_all:
                reply_message = "Desculpe, verifiquei novamente e realmente não há horários disponíveis no momento. Por favor, entre em contato conosco diretamente para verificar futuras disponibilidades."
                new_state = "HUMAN_TAKEOVER" # Escalate if even showing all yields nothing
                state_service.save_state(phone_number, new_state, context)
            else:
                # Format all available slots
                slot_options = []
                for slot in available_slots_all:
                    try:
                        from datetime import datetime
                        start_dt = datetime.fromisoformat(slot['start_time'])
                        formatted_time = start_dt.strftime("%d/%m/%Y às %H:%M")
                        slot_options.append(f"- {formatted_time} (ID: {slot['slot_id']})")
                    except (ValueError, KeyError):
                        slot_options.append(f"- Horário inválido (ID: {slot.get('slot_id', 'N/A')})")

                reply_message = "Ok, aqui estão todos os horários disponíveis:\n" + "\n".join(slot_options) + "\n\nPor favor, digite o ID do horário que deseja escolher."
                new_state = "AWAITING_SLOT_CHOICE"
                state_service.save_state(phone_number, new_state, new_context)

        except Exception as e:
            print(f"Error fetching or formatting all slots in AWAITING_SLOT_PREFERENCE_ALL: {e}")
            reply_message = "Ocorreu um erro ao buscar os horários. Por favor, tente novamente mais tarde."
            # Go back to AWAITING_SLOT_PREFERENCE? Or stay here?
            new_state = "AWAITING_SLOT_PREFERENCE" # Let them restart the preference process
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

# --- Send Confirmation Message Endpoint --- 

class ConfirmationPayload(BaseModel):
   phone_number: str = Field(..., description="Patient's phone number with country code")
   patient_name: str = Field(..., description="Patient's full name")
   appointment_details: str = Field(..., description="Confirmed appointment date and time (e.g., '15 de agosto de 2024 às 10:30')")

@router.post("/send-confirmation")
async def send_confirmation_message(payload: ConfirmationPayload):
   """
   Endpoint to trigger sending a confirmation message after successful booking.
   This should be called by the backend/admin system after verification.
   """
   print(f"Received request to send confirmation to {payload.phone_number}")
   whatsapp_service = WhatsAppService()

   # Format the confirmation message
   # TODO: Consider making this message template configurable
   confirmation_message = (
       f"Olá {payload.patient_name}, seu agendamento para {payload.appointment_details} foi confirmado com sucesso! "
       f"Aguardamos você."
   )

   try:
       await whatsapp_service.send_message(payload.phone_number, confirmation_message)
       print(f"Confirmation message sent successfully to {payload.phone_number}.")
       # Optionally, update the conversation state here if desired
       # state_service = ConversationStateService()
       # state_service.save_state(payload.phone_number, "COMPLETED", {}) 
       return {"status": "success", "message": "Confirmation sent."}
   except Exception as e:
       print(f"Error sending confirmation message to {payload.phone_number}: {e}")
       raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail=f"Failed to send confirmation message: {str(e)}",
       )