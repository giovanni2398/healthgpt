from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from app.api import whatsapp, calendar, notifications, conversation

load_dotenv()

from app.api.whatsapp import router as whatsapp_router
from app.api.conversation import router as conversation_router

app = FastAPI(title="HealthGPT")

# Configura os templates
templates = Jinja2Templates(directory="app/templates")

# Inclui os routers
app.include_router(whatsapp.router, prefix="/whatsapp")
app.include_router(calendar.router, prefix="/calendar")
app.include_router(conversation_router, prefix="/conversation")
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(conversation.router, prefix="/api/conversation", tags=["conversation"])

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial da aplicação."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request):
    """Página de logs de notificações."""
    return templates.TemplateResponse("notification_logs.html", {"request": request})
