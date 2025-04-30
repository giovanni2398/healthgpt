from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.api.whatsapp import router as whatsapp_router

app = FastAPI(title="HealthGPT API")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui apenas o router essencial
app.include_router(whatsapp_router, prefix="/whatsapp")

@app.get("/")
async def home():
    """Endpoint básico para verificar se a API está funcionando."""
    return {"status": "API operacional", "message": "Bem-vindo ao HealthGPT"}
