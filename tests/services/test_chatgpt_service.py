import pytest
from unittest.mock import patch, MagicMock
from app.services.chatgpt_service import ChatGPTService
from app.config.config import ACCEPTED_INSURANCE_PROVIDERS

@pytest.fixture
def mock_openai_response():
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Test response"
            )
        )
    ]
    return mock_response

@pytest.fixture
def mock_openai_client():
    with patch('openai.OpenAI') as mock_client:
        mock_instance = MagicMock()
        mock_instance.chat = MagicMock()
        mock_instance.chat.completions = MagicMock()
        mock_instance.chat.completions.create = MagicMock()
        mock_client.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def chatgpt_service(mock_openai_client):
    with patch('app.services.chatgpt_service.OPENAI_API_KEY', 'test_key'):
        service = ChatGPTService()
        service.client = mock_openai_client
        return service

def test_generate_response(chatgpt_service, mock_openai_response):
    # Arrange
    prompt = "Hello"
    system_message = "You are a test assistant"
    chatgpt_service.client.chat.completions.create.return_value = mock_openai_response

    # Act
    response = chatgpt_service.generate_response(prompt, system_message)

    # Assert
    assert response == "Test response"
    chatgpt_service.client.chat.completions.create.assert_called_once()
    call_args = chatgpt_service.client.chat.completions.create.call_args[1]
    assert call_args['messages'] == [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

def test_analyze_patient_type_insurance(chatgpt_service, mock_openai_response):
    # Arrange
    message = "I want to schedule with my Unimed insurance"
    mock_openai_response.choices[0].message.content = '''
    {
        "type": "insurance",
        "insurance_name": "Unimed",
        "confidence": 0.95
    }
    '''
    chatgpt_service.client.chat.completions.create.return_value = mock_openai_response

    # Act
    result = chatgpt_service.analyze_patient_type(message)

    # Assert
    assert result["type"] == "insurance"
    assert result["insurance_name"] == "Unimed"
    assert result["confidence"] == 0.95

def test_analyze_patient_type_private(chatgpt_service, mock_openai_response):
    # Arrange
    message = "I want to schedule a private appointment"
    mock_openai_response.choices[0].message.content = '''
    {
        "type": "private",
        "insurance_name": null,
        "confidence": 0.9
    }
    '''
    chatgpt_service.client.chat.completions.create.return_value = mock_openai_response

    # Act
    result = chatgpt_service.analyze_patient_type(message)

    # Assert
    assert result["type"] == "private"
    assert result["insurance_name"] is None
    assert result["confidence"] == 0.9

def test_validate_insurance_accepted():
    # Arrange
    service = ChatGPTService()
    insurance_name = ACCEPTED_INSURANCE_PROVIDERS[0]

    # Act
    result = service.validate_insurance(insurance_name)

    # Assert
    assert result is True

def test_validate_insurance_not_accepted():
    # Arrange
    service = ChatGPTService()
    insurance_name = "Invalid Insurance"

    # Act
    result = service.validate_insurance(insurance_name)

    # Assert
    assert result is False

def test_generate_response_error(chatgpt_service):
    # Arrange
    chatgpt_service.client.chat.completions.create.side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        chatgpt_service.generate_response("test")
    assert "Error generating response" in str(exc_info.value)

def test_analyze_patient_type_invalid_json(chatgpt_service, mock_openai_response):
    # Arrange
    mock_openai_response.choices[0].message.content = "Invalid JSON"
    chatgpt_service.client.chat.completions.create.return_value = mock_openai_response

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        chatgpt_service.analyze_patient_type("test")
    assert "Error analyzing patient type" in str(exc_info.value) 