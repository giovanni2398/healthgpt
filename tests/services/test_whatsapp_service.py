import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import httpx # Import for type hinting and potentially mocking response object
import os # Import the os module

from app.services.whatsapp_service import WhatsAppService


@pytest.fixture
def mock_chatgpt_service():
    with patch('app.services.whatsapp_service.ChatGPTService') as mock:
        instance = mock.return_value
        instance.generate_response = MagicMock(return_value="Mocked ChatGPT response")
        yield instance


@pytest.fixture
def whatsapp_service(mock_chatgpt_service):
    # Patch environment variables needed for service initialization
    with patch.dict(os.environ, {
        "WHATSAPP_API_TOKEN": "test_token", 
        "WHATSAPP_PHONE_NUMBER_ID": "test_phone_id"
        # Add OPENAI_API_KEY if ChatGPTService fixture doesn't handle it
        # "OPENAI_API_KEY": "test_openai_key" 
    }):
        service = WhatsAppService()
        service.chatgpt_service = mock_chatgpt_service
        return service


def test_receive_message(whatsapp_service):
    # Arrange
    payload = {"from": "+5511999999999", "text": "Olá, quero agendar"}

    # Act
    result = whatsapp_service.receive_message(payload)

    # Assert
    assert result["phone"] == "+5511999999999"
    assert result["text"] == "Olá, quero agendar"
    assert result["response"] == "Mocked ChatGPT response"
    whatsapp_service.chatgpt_service.generate_response.assert_called_once()


@patch('httpx.Client.post') # Patch the post method
def test_send_message(mock_post, whatsapp_service):
    # Arrange
    phone = "+5511999999999"
    message = "Test message"
    expected_url = whatsapp_service.api_url
    expected_headers = {
        "Authorization": f"Bearer {whatsapp_service.token}",
        "Content-Type": "application/json",
    }
    expected_payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message}
    }
    
    # Configure the mock response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"messaging_product": "whatsapp", "contacts": [], "messages": []} # Example success response
    mock_post.return_value = mock_response

    # Act
    result = whatsapp_service.send_message(phone, message)

    # Assert
    assert result is True
    mock_post.assert_called_once_with(expected_url, headers=expected_headers, json=expected_payload)
    mock_response.raise_for_status.assert_called_once() # Ensure status check was performed


@patch('httpx.Client.post') # Patch the post method
def test_send_appointment_confirmation(mock_post, whatsapp_service):
    # Arrange
    phone = "+5511999999999"
    patient_name = "João"
    appointment_date = datetime(2024, 4, 1, 14, 30)
    reason = "Consulta de rotina"
    
    # Expected message content (formatted inside the method)
    formatted_date = appointment_date.strftime("%d/%m/%Y às %H:%M")
    expected_message_body = (
        f"✅ Agendamento Confirmado!\n\n"
        f"Olá {patient_name},\n\n"
        f"Seu agendamento foi confirmado para:\n"
        f"📅 Data: {formatted_date}\n"
        f"📝 Motivo: {reason}\n\n"
        f"Se precisar reagendar ou cancelar, entre em contato conosco.\n"
        f"Até breve! 👋"
    )
    expected_payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": expected_message_body}
    }
    
    # Configure mock response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    # Act
    result = whatsapp_service.send_appointment_confirmation(
        phone, patient_name, appointment_date, reason
    )

    # Assert
    assert result is True
    # Assert httpx.post was called correctly by the internal send_message call
    mock_post.assert_called_once()
    call_args = mock_post.call_args[1] # Get keyword args
    assert call_args['json'] == expected_payload
    mock_response.raise_for_status.assert_called_once()


# Optional: Add tests for failure cases (e.g., API returning non-200 status)
@patch('httpx.Client.post')
def test_send_message_api_failure(mock_post, whatsapp_service):
    # Arrange
    phone = "+5511999999999"
    message = "Test failure"
    
    # Configure the mock response for failure
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 400 # Simulate a client error
    mock_response.text = "Bad Request Error Text"
    # Make raise_for_status raise the appropriate error
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Client error '400 Bad Request' for url 'mock://url'", 
        request=MagicMock(), 
        response=mock_response
    )
    mock_post.return_value = mock_response

    # Act
    result = whatsapp_service.send_message(phone, message)

    # Assert
    assert result is False # Expect failure
    mock_post.assert_called_once()
    mock_response.raise_for_status.assert_called_once() 