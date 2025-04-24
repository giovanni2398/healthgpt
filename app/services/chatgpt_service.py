import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

# Aqui poderíamos usar a biblioteca openai, mas ainda vamos simular:
# from openai import OpenAI

class ChatGPTService:
    """
    Serviço que encapsula a comunicação com o ChatGPT.
    Por enquanto, estamos criando um MOCK: respostas pré-definidas,
    para validar nosso fluxo de requisição/resposta.
    """

    def __init__(self):
        # No futuro: carregar API_KEY, instanciar cliente OpenAI
        # self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        pass

    def generate_response(self, prompt: str) -> str:
        """
        Recebe o prompt (mensagem do paciente) e retorna uma resposta simulada.
        Em produção vamos substituir esse método para chamar a API da OpenAI.
        """
        # MOCK simples: ecoar o prompt + texto fixo
        return f"Mocked response to: «{prompt}». Em breve, aqui virá a resposta do ChatGPT real."
