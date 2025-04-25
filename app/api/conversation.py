# Import necessary modules and classes
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import services for WhatsApp, calendar, and ChatGPT
from app.services.whatsapp_service import WhatsAppService
# Import calendar service functions for managing appointments
from app.services.calendar_service import get_calendar_service, get_available_slots
from app.services.chatgpt_service import ChatGPTService

# Initialize FastAPI router
router = APIRouter()

# Instantiate service objects
wa_service = WhatsAppService()  # WhatsApp service for sending messages
chatgpt_service = ChatGPTService()  # ChatGPT service for generating responses

# Define request model for conversation API
class ConversationRequest(BaseModel):
    from_: str  # Sender's identifier (e.g., phone number)
    message: str  # Message content

# Define response model for conversation API
class ConversationResponse(BaseModel):
    reply: str  # Reply message content

# Define API endpoint to handle conversation messages
@router.post("/message", response_model=ConversationResponse)
async def handle_conversation(req: ConversationRequest):
    try:
        # Step 1: Receive message and identify intent using ChatGPT
        intent = chatgpt_service.generate_response(req.message)

        # Step 2: Check basic intent (whether it's "particular" or "convênio")
        if "convênio" in intent.lower():
            # If intent mentions "convênio", ask for the user's health plan
            reply = "Qual é o seu convênio?"
        elif "particular" in intent.lower():
            # If intent mentions "particular", provide available slots for a specific date
            available_slots = get_available_slots("2025-04-25")
            reply = f"Temos os seguintes horários: {available_slots}"
        else:
            # If intent is unclear, ask for clarification
            reply = "Você deseja atendimento particular ou por convênio?"

        # Step 3: Send the reply via WhatsApp
        wa_service.send_message(req.from_, reply)

        # Return the reply as the API response
        return ConversationResponse(reply=reply)
    except Exception as e:
        # Handle any exceptions and return a 500 error with the exception details
        raise HTTPException(status_code=500, detail=str(e))
