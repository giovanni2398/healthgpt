import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.services.whatsapp_service import WhatsAppService


@pytest.fixture
def mock_chatgpt_service():
    with patch('app.services.whatsapp_service.ChatGPTService') as mock:
        instance = mock.return_value
        instance.generate_response = MagicMock(return_value="Test response")
        yield instance


@pytest.fixture
def whatsapp_service(mock_chatgpt_service):
    with patch('os.getenv', return_value="test_token"):
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
    assert result["response"] == "Test response"
    whatsapp_service.chatgpt_service.generate_response.assert_called_once()


def test_send_message(whatsapp_service):
    # Arrange
    phone = "+5511999999999"
    message = "Test message"

    # Act
    result = whatsapp_service.send_message(phone, message)

    # Assert
    assert result is True


def test_send_appointment_confirmation(whatsapp_service):
    # Arrange
    phone = "+5511999999999"
    patient_name = "João"
    appointment_date = datetime(2024, 4, 1, 14, 30)
    reason = "Consulta de rotina"

    # Act
    result = whatsapp_service.send_appointment_confirmation(
        phone, patient_name, appointment_date, reason
    )

    # Assert
    assert result is True


def test_send_message_returns_true_and_prints(capfd):
    service = WhatsAppService()
    phone = "+5511999999999"
    message = "Test message"
    result = service.send_message(phone, message)
    assert result is True
    captured = capfd.readouterr()
    # Verifica que o print mock incluiu o prefixo correto
    assert f"[MOCK] Enviar para {phone}: {message}" in captured.out


def test_send_appointment_confirmation_monkeypatch(monkeypatch):
    service = WhatsAppService()
    called = {}
    def fake_send(phone, msg):
        called['phone'] = phone
        called['message'] = msg
        return False
    # Substitui o método send_message por fake_send
    monkeypatch.setattr(service, 'send_message', fake_send)
    phone = "+5511999999999"
    name = "Maria"
    appt_date = datetime(2025, 1, 1, 10, 0)
    reason = "Consulta"
    result = service.send_appointment_confirmation(phone, name, appt_date, reason)
    assert result is False  # porque fake_send retorna False
    assert called['phone'] == phone
    # Valida que a mensagem contém nome, data formatada e motivo
    assert name in called['message']
    formatted = appt_date.strftime("%d/%m/%Y às %H:%M")
    assert formatted in called['message']
    assert reason in called['message'] 