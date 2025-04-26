import os
import pytest
from unittest.mock import patch, MagicMock
from app.services.chatgpt_service import ChatGPTService

def test_chatgpt_service_initialization():
    # Test successful initialization
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        service = ChatGPTService()
        assert service.api_key == "test_key"
        assert service.client is not None

    # Test initialization without API key
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            ChatGPTService()
        assert "OPENAI_API_KEY não encontrada nas variáveis de ambiente" in str(exc_info.value)

@patch('app.services.chatgpt_service.OpenAI')
def test_generate_response_success(mock_openai):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    # Test successful response generation
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        service = ChatGPTService()
        response = service.generate_response("Test prompt")
        
        assert response == "Test response"
        mock_openai.return_value.chat.completions.create.assert_called_once()

@patch('app.services.chatgpt_service.OpenAI')
def test_generate_response_error_handling(mock_openai):
    # Setup mock to raise an exception
    mock_openai.return_value.chat.completions.create.side_effect = Exception("Test error")

    # Test error handling
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        service = ChatGPTService()
        response = service.generate_response("Test prompt")
        
        assert "Desculpe, ocorreu um erro ao processar sua mensagem" in response
        assert "Test error" in response
