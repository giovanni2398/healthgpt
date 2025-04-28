import pytest
from types import SimpleNamespace

import os
from dotenv import load_dotenv
from app.services.chatgpt_service import ChatGPTService


def test_generate_response_success(monkeypatch):
    """
    Testa se generate_response retorna corretamente o conteúdo 'choices[0].message.content'
    quando a chamada ao cliente da OpenAI for bem sucedida.
    """
    # Define a variável de ambiente para a chave da API
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    # Cria um fake response structure
    fake_message = SimpleNamespace(content="Resposta simulada")
    fake_choice = SimpleNamespace(message=fake_message)
    fake_response = SimpleNamespace(choices=[fake_choice])

    # Instancia o serviço
    service = ChatGPTService()

    # Substitui o método create no cliente de chat
    monkeypatch.setattr(
        service.client.chat.completions,
        'create',
        lambda *args, **kwargs: fake_response
    )

    # Chama o método e verifica saída
    result = service.generate_response("Olá, ChatGPT!")
    assert result == "Resposta simulada"


def test_generate_response_error(monkeypatch):
    """
    Testa se generate_response retorna mensagem de erro customizada contendo o texto da exceção
    quando a chamada ao cliente da OpenAI lança uma exceção.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    service = ChatGPTService()

    # Simula exceção na API
    def fake_create(*args, **kwargs):
        raise Exception("API indisponível")

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        service.client.chat.completions,
        'create',
        fake_create
    )

    # Chama o método
    result = service.generate_response("Teste de erro")
    assert "Desculpe, ocorreu um erro" in result
    assert "API indisponível" in result 