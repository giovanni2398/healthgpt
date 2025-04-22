from fastapi import FastAPI
from app.api import whatsapp, calendar, chatgpt

app = FastAPI(title="HealthGPT")

app.include_router(whatsapp.router, prefix="/whatsapp")
app.include_router(calendar.router, prefix="/calendar")
app.include_router(chatgpt.router, prefix="/chatgpt")
