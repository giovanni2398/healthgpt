import pytest
from datetime import datetime

from app.services.whatsapp_service import WhatsAppService


def test_receive_message_echo():
    service = WhatsAppService()
    payload = {"from": "+5511999999999", "text": "Olá!"}
    result = service.receive_message(payload)
    assert result["phone"] == "+5511999999999"
    assert result["text"] == "Olá!"


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