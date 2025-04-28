import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.services.appointment_orchestrator import AppointmentOrchestrator
from app.services.notification_service import NotificationService
from app.services.notification_log_service import NotificationLogService
from app.services.whatsapp_service import WhatsAppService
from app.services.calendar_service import get_available_slots, create_calendar_event, get_calendar_service

@pytest.fixture
def mock_calendar_slots():
    """Simula slots disponíveis no calendário."""
    date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    return [
        datetime.fromisoformat(f"{date}T09:00:00"),
        datetime.fromisoformat(f"{date}T10:00:00"),
        datetime.fromisoformat(f"{date}T11:00:00"),
        datetime.fromisoformat(f"{date}T14:00:00"),
        datetime.fromisoformat(f"{date}T15:00:00"),
    ]

@pytest.fixture
def mock_calendar_event():
    """Simula um evento criado no calendário."""
    return {
        'id': 'test_event_id',
        'htmlLink': 'https://calendar.google.com/test_event',
        'status': 'confirmed'
    }

@pytest.fixture
def setup_services():
    """Configura os serviços necessários para os testes."""
    orchestrator = AppointmentOrchestrator()
    whatsapp_service = WhatsAppService()
    notification_service = NotificationService(whatsapp_service)
    log_service = NotificationLogService()
    
    return {
        'orchestrator': orchestrator,
        'whatsapp_service': whatsapp_service,
        'notification_service': notification_service,
        'log_service': log_service
    }

@pytest.fixture
def test_data():
    """Fornece dados de teste comuns."""
    return {
        'patient_id': '123',
        'patient_name': "João Silva",
        'patient_phone': "+5511999999999",
        'insurance': "Unimed",
        'appointment_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        'appointment_time': "09:00",
        'reason': "Consulta nutricional"
    }

class TestAppointmentFlow:
    """Testes para o fluxo completo de agendamento."""
    
    @patch('app.services.whatsapp_service.WhatsAppService.send_message', new_callable=MagicMock)
    @patch('app.services.whatsapp_service.WhatsAppService.send_appointment_confirmation', new_callable=MagicMock)
    @patch('app.services.calendar_service.create_calendar_event', new_callable=MagicMock)
    def test_successful_insurance_appointment(
        self, mock_create_event, mock_send_confirmation, mock_send_message,
        setup_services, test_data, mock_calendar_slots, mock_calendar_event
    ):
        """Testa o fluxo completo de agendamento com convênio válido."""
        # Configura mocks
        mock_send_message.return_value = True
        mock_send_confirmation.return_value = True
        mock_create_event.return_value = mock_calendar_event
        
        # Cria slot para teste
        start_time = datetime.strptime(f"{test_data['appointment_date']} {test_data['appointment_time']}", "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=1)
        slot_id = setup_services['orchestrator'].scheduling_service.slot_service.create_slot(
            start_time=start_time,
            end_time=end_time
        )
        
        # Tenta agendar
        success = setup_services['orchestrator'].schedule_appointment(
            patient_id=test_data['patient_id'],
            patient_name=test_data['patient_name'],
            patient_phone=test_data['patient_phone'],
            slot_id=slot_id,
            reason=test_data['reason'],
            is_private=False,
            insurance=test_data['insurance'],
            insurance_card_url="https://example.com/insurance.pdf",
            id_document_url="https://example.com/id.pdf"
        )
        
        # Verifica se o agendamento foi bem sucedido
        assert success is True
        
        # Verifica se as mensagens foram enviadas
        mock_send_confirmation.assert_called_once()
    
    @patch('app.services.whatsapp_service.WhatsAppService.send_message', new_callable=MagicMock)
    @patch('app.services.whatsapp_service.WhatsAppService.send_appointment_confirmation', new_callable=MagicMock)
    @patch('app.services.calendar_service.create_calendar_event', new_callable=MagicMock)
    def test_private_appointment_flow(
        self, mock_create_event, mock_send_confirmation, mock_send_message,
        setup_services, test_data, mock_calendar_slots, mock_calendar_event
    ):
        """Testa o fluxo de agendamento particular."""
        # Configura mocks
        mock_send_message.return_value = True
        mock_send_confirmation.return_value = True
        mock_create_event.return_value = mock_calendar_event
        
        # Cria slot para teste
        start_time = datetime.strptime(f"{test_data['appointment_date']} {test_data['appointment_time']}", "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=1)
        slot_id = setup_services['orchestrator'].scheduling_service.slot_service.create_slot(
            start_time=start_time,
            end_time=end_time
        )
        
        # Tenta agendar
        success = setup_services['orchestrator'].schedule_appointment(
            patient_id=test_data['patient_id'],
            patient_name=test_data['patient_name'],
            patient_phone=test_data['patient_phone'],
            slot_id=slot_id,
            reason=test_data['reason'],
            is_private=True,
            id_document_url="https://example.com/id.pdf"
        )
        
        # Verifica se o agendamento foi bem sucedido
        assert success is True
        
        # Verifica se as mensagens foram enviadas
        mock_send_confirmation.assert_called_once()
    
    @patch('app.services.whatsapp_service.WhatsAppService.send_message', new_callable=MagicMock)
    def test_appointment_flow_with_invalid_insurance(
        self, mock_send_message,
        setup_services, test_data
    ):
        """Testa o fluxo de agendamento com convênio inválido."""
        # Configura mock
        mock_send_message.return_value = True
        
        # Cria slot para teste
        start_time = datetime.strptime(f"{test_data['appointment_date']} {test_data['appointment_time']}", "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=1)
        slot_id = setup_services['orchestrator'].scheduling_service.slot_service.create_slot(
            start_time=start_time,
            end_time=end_time
        )
        
        # Tenta agendar com convênio inválido
        success = setup_services['orchestrator'].schedule_appointment(
            patient_id=test_data['patient_id'],
            patient_name=test_data['patient_name'],
            patient_phone=test_data['patient_phone'],
            slot_id=slot_id,
            reason=test_data['reason'],
            is_private=False,
            insurance="Convênio Inválido",
            insurance_card_url="https://example.com/insurance.pdf",
            id_document_url="https://example.com/id.pdf"
        )
        
        # Verifica se o agendamento falhou
        assert success is False
        
        # Verifica se a mensagem de erro foi enviada
        mock_send_message.assert_called_with(
            test_data['patient_phone'],
            "Desculpe, mas não atendemos este convênio. Por favor, verifique os convênios aceitos."
        ) 