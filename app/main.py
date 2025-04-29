from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from app.api import whatsapp, calendar, notifications, conversation, slots, simplified_slots

load_dotenv()

from app.api.whatsapp import router as whatsapp_router
from app.api.conversation import router as conversation_router
from app.api.slots import router as slots_router
from app.api.simplified_slots import router as simplified_slots_router

app = FastAPI(title="HealthGPT API")

# Configura os templates
templates = Jinja2Templates(directory="app/templates")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Substitua por origens específicas em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os routers
app.include_router(whatsapp.router, prefix="/whatsapp")
app.include_router(calendar.router, prefix="/calendar")
app.include_router(conversation_router, prefix="/conversation")
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(conversation.router, prefix="/api/conversation", tags=["conversation"])
app.include_router(slots_router, tags=["slots"])  # Endpoint já possui o prefixo /slots
app.include_router(simplified_slots_router, tags=["simplified-slots"])  # Router já possui o prefixo /api/simplified-slots

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página inicial da aplicação."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/notifications", response_class=HTMLResponse)
async def notifications_page(request: Request):
    """Página de logs de notificações."""
    return templates.TemplateResponse("notification_logs.html", {"request": request})
