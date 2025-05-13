from fastapi import FastAPI, Request
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
async def home(request: Request):
    """Endpoint básico para verificar se a API está funcionando."""
    print(f"Received request at ROOT (/): URL={request.url}, Headers={request.headers}")
    return {"status": "API operacional", "message": "Bem-vindo ao HealthGPT"}
