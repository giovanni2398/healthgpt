import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

from openai import OpenAI

class ChatGPTService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY não encontrada nas variáveis de ambiente")
        self.client = OpenAI(api_key=self.api_key) 

    def generate_response(self, prompt: str) -> str:
        """
        Gera uma resposta usando a API da OpenAI baseada no prompt fornecido.
        O prompt é a mensagem do paciente que precisa ser analisada.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente de agendamento para uma clínica de nutrição. Sua função é ajudar os pacientes a marcarem consultas, entenderem seus planos de tratamento e responderem dúvidas sobre nutrição de forma geral. Mantenha as respostas profissionais, claras e objetivas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente mais tarde. Erro: {str(e)}"
