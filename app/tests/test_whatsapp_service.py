from datetime import datetime, timedelta
import pytest
from unittest.mock import Mock, patch
from app.services.whatsapp_service import WhatsAppService
from app.services.conversation_state import ConversationState

@pytest.fixture
def whatsapp_service():
    """Fixture para criar uma instância do WhatsAppService para testes"""
    with patch('app.services.whatsapp_service.ChatGPTService') as mock_chatgpt, \
         patch('app.services.whatsapp_service.CalendarService') as mock_calendar:
        service = WhatsAppService()
        service.chatgpt_service = mock_chatgpt.return_value
        service.calendar_service = mock_calendar.return_value
        yield service

def test_receive_message_initial_state(whatsapp_service):
    """Testa o processamento de mensagem no estado inicial"""
    # Configura o mock do ChatGPT
    whatsapp_service.chatgpt_service.generate_response.return_value = "Olá! Como posso ajudar?"
    
    # Processa a mensagem
    result = whatsapp_service.receive_message({
        "from": "5511999999999",
        "text": "Olá"
    })
    
    # Verifica o resultado
    assert result["phone"] == "5511999999999"
    assert result["text"] == "Olá"
    assert result["state"] == ConversationState.INITIAL.value

def test_receive_message_with_insurance(whatsapp_service):
    """Testa o processamento de mensagem com convênio aceito"""
    # Configura o mock do ChatGPT
    whatsapp_service.chatgpt_service.generate_response.return_value = "CONVENIO: unimed"
    
    # Processa a mensagem
    result = whatsapp_service.receive_message({
        "from": "5511999999999",
        "text": "Quero agendar com Unimed"
    })
    
    # Verifica o resultado
    assert result["state"] == ConversationState.WAITING_FOR_INSURANCE_DOCS.value
    assert whatsapp_service.conversation_manager.get_data("5511999999999")["insurance"] == "unimed"
    assert "carteirinha" in result["response"].lower()
    assert "documento" in result["response"].lower()

def test_receive_message_with_invalid_insurance(whatsapp_service):
    """Testa o processamento de mensagem com convênio não aceito"""
    # Configura o mock do ChatGPT
    whatsapp_service.chatgpt_service.generate_response.return_value = "CONVENIO: nao_aceito"
    
    # Processa a mensagem
    result = whatsapp_service.receive_message({
        "from": "5511999999999",
        "text": "Quero agendar com um convênio não aceito"
    })
    
    # Verifica o resultado
    assert result["state"] == ConversationState.INITIAL.value
    assert "não trabalhamos" in result["response"].lower()
    assert "consulta particular" in result["response"].lower()

def test_receive_message_with_particular(whatsapp_service):
    """Testa o processamento de mensagem com particular"""
    # Configura o mock do ChatGPT
    whatsapp_service.chatgpt_service.generate_response.return_value = "PARTICULAR: sim"
    
    # Processa a mensagem
    result = whatsapp_service.receive_message({
        "from": "5511999999999",
        "text": "Quero agendar particular"
    })
    
    # Verifica o resultado
    assert result["state"] == ConversationState.WAITING_FOR_DATE.value
    assert whatsapp_service.conversation_manager.get_data("5511999999999")["insurance"] == "particular"
    assert "consulta inicial" in result["response"].lower()
    assert "retorno" in result["response"].lower()
    assert "pacote" in result["response"].lower()

def test_receive_message_with_date(whatsapp_service):
    """Testa o processamento de mensagem com data"""
    # Configura o mock do ChatGPT
    whatsapp_service.chatgpt_service.generate_response.return_value = "DATA_MENCIONADA: 2024-05-01"
    
    # Processa a mensagem
    result = whatsapp_service.receive_message({
        "from": "5511999999999",
        "text": "Quero agendar para dia 1 de maio"
    })
    
    # Verifica o resultado
    assert result["state"] == ConversationState.WAITING_FOR_TIME.value
    assert whatsapp_service.conversation_manager.get_data("5511999999999")["date"] == "2024-05-01"

def test_receive_message_with_time(whatsapp_service):
    """Testa o processamento de mensagem com horário"""
    # Configura o estado inicial
    whatsapp_service.conversation_manager.set_state("5511999999999", ConversationState.WAITING_FOR_TIME)
    whatsapp_service.conversation_manager.update_data("5511999999999", {"date": "2024-05-01"})
    
    # Configura o mock do ChatGPT
    whatsapp_service.chatgpt_service.generate_response.return_value = "HORARIO_MENCIONADO: 14:30"
    
    # Processa a mensagem
    result = whatsapp_service.receive_message({
        "from": "5511999999999",
        "text": "Quero agendar para as 14:30"
    })
    
    # Verifica o resultado
    assert result["state"] == ConversationState.WAITING_FOR_CONFIRMATION.value
    assert whatsapp_service.conversation_manager.get_data("5511999999999")["time"] == "14:30"

def test_receive_message_with_confirmation(whatsapp_service):
    """Testa o processamento de mensagem com confirmação"""
    # Configura o estado inicial
    whatsapp_service.conversation_manager.set_state("5511999999999", ConversationState.WAITING_FOR_CONFIRMATION)
    whatsapp_service.conversation_manager.update_data("5511999999999", {
        "date": "2024-05-01",
        "time": "14:30",
        "insurance": "unimed"
    })
    
    # Configura os mocks
    whatsapp_service.chatgpt_service.generate_response.return_value = "CONFIRMACAO: sim"
    whatsapp_service.calendar_service.create_calendar_event.return_value = True
    whatsapp_service.send_message = Mock(return_value=True)
    
    # Processa a mensagem
    result = whatsapp_service.receive_message({
        "from": "5511999999999",
        "text": "Sim, quero confirmar"
    })
    
    # Verifica o resultado
    assert result["state"] == ConversationState.COMPLETED.value
    whatsapp_service.calendar_service.create_calendar_event.assert_called_once()
    whatsapp_service.send_message.assert_called()

def test_send_message_success(whatsapp_service):
    """Testa o envio de mensagem com sucesso"""
    with patch('httpx.Client') as mock_client:
        # Configura o mock
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "123"}
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        
        # Envia a mensagem
        result = whatsapp_service.send_message("5511999999999", "Teste")
        
        # Verifica o resultado
        assert result == True

def test_send_message_failure(whatsapp_service):
    """Testa o envio de mensagem com falha"""
    with patch('httpx.Client') as mock_client:
        # Configura o mock
        mock_response = Mock()
        mock_response.status_code = 500
        mock_client.return_value.__enter__.return_value.post.return_value = mock_response
        
        # Envia a mensagem
        result = whatsapp_service.send_message("5511999999999", "Teste")
        
        # Verifica o resultado
        assert result == False

def test_send_appointment_confirmation(whatsapp_service):
    """Testa o envio de confirmação de agendamento"""
    # Configura o mock
    whatsapp_service.send_message = Mock(return_value=True)
    
    # Envia a confirmação
    appointment_date = datetime.now()
    result = whatsapp_service.send_appointment_confirmation(
        phone="5511999999999",
        patient_name="João",
        appointment_date=appointment_date,
        reason="Consulta de Nutrição - Unimed"
    )
    
    # Verifica o resultado
    assert result == True
    whatsapp_service.send_message.assert_called_once() 