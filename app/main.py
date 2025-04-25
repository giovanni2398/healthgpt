from fastapi import FastAPI
from app.api import whatsapp, calendar, chatgpt
from dotenv import load_dotenv
load_dotenv()

from app.api.whatsapp import router as whatsapp_router
from app.api.conversation import router as conversation_router

app = FastAPI(title="HealthGPT")

app.include_router(whatsapp.router, prefix="/whatsapp")
app.include_router(calendar.router, prefix="/calendar")
app.include_router(chatgpt.router, prefix="/chatgpt")
app.include_router(conversation_router, prefix="/conversation")
