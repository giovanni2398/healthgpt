import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.services.appointment_orchestrator import AppointmentOrchestrator
from app.services.notification_service import NotificationService
from app.services.notification_log_service import NotificationLogService
from app.services.whatsapp_service import WhatsAppService
from app.services.calendar_service import get_available_slots, create_calendar_event, get_calendar_service

# Mock para simular slots disponíveis
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

# Mock para simular evento criado
@pytest.fixture
def mock_calendar_event():
    """Simula um evento criado no calendário."""
    return {
        'id': 'test_event_id',
        'htmlLink': 'https://calendar.google.com/test_event',
        'status': 'confirmed'
    }

# Mock para o serviço do Google Calendar
@pytest.fixture
def mock_calendar_service():
    """Cria um mock completo do serviço do Google Calendar."""
    mock_service = MagicMock()
    
    # Mock para events().list().execute()
    mock_list = MagicMock()
    mock_list.execute = MagicMock(return_value={'items': []})
    
    # Mock para events().insert().execute()
    mock_insert = MagicMock()
    mock_insert.execute = MagicMock(return_value={
        'id': 'test_event_id',
        'htmlLink': 'https://calendar.google.com/test_event',
        'status': 'confirmed'
    })
    
    # Configura a estrutura do serviço mockado
    mock_events = MagicMock()
    mock_events.list = MagicMock(return_value=mock_list)
    mock_events.insert = MagicMock(return_value=mock_insert)
    mock_service.events = MagicMock(return_value=mock_events)
    
    return mock_service

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
        'patient_name': "João Silva",
        'patient_phone': "+5511999999999",
        'insurance': "Unimed",
        'appointment_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        'appointment_time': "09:00"
    }

class TestAppointmentFlow:
    """Testes para o fluxo completo de agendamento."""
    
    @patch('app.services.whatsapp_service.WhatsAppService.send_message')
    @patch('app.services.calendar_service.get_calendar_service')
    def test_successful_insurance_appointment(
        self, mock_get_service, mock_send_message,
        setup_services, test_data, mock_calendar_slots, mock_calendar_event, mock_calendar_service
    ):
        """Testa o fluxo completo de agendamento com convênio válido."""
        # Configura mocks
        mock_send_message.return_value = True
        mock_get_service.return_value = mock_calendar_service
        
        # 1. Identifica tipo de paciente
        patient_type = setup_services['orchestrator'].identify_patient_type(test_data['insurance'])
        assert patient_type == "insurance"
        
        # 2. Valida convênio
        is_valid_insurance = setup_services['orchestrator'].validate_insurance(test_data['insurance'])
        assert is_valid_insurance
        
        # 3. Verifica disponibilidade
        start_time = datetime.strptime(f"{test_data['appointment_date']} {test_data['appointment_time']}", "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=1)
        
        # 4. Cria agendamento
        event = create_calendar_event(
            start_time,
            end_time,
            test_data['patient_name'],
            test_data['patient_phone'],
            f"Consulta - {test_data['insurance']}"
        )
        
        assert event is not None
        assert 'id' in event
        assert event['id'] == 'test_event_id'
        
        # 5. Envia confirmação
        confirmation_message = f"Agendamento confirmado para {test_data['appointment_date']} às {test_data['appointment_time']}"
        setup_services['whatsapp_service'].send_message(test_data['patient_phone'], confirmation_message)
        
        # Verifica se a mensagem foi enviada
        mock_send_message.assert_called_with(test_data['patient_phone'], confirmation_message)
    
    @patch('app.services.whatsapp_service.WhatsAppService.send_message')
    @patch('app.services.calendar_service.get_calendar_service')
    def test_private_patient_appointment(
        self, mock_get_service, mock_send_message,
        setup_services, test_data, mock_calendar_slots, mock_calendar_event, mock_calendar_service
    ):
        """Testa o fluxo de agendamento para paciente particular."""
        # Configura mocks
        mock_send_message.return_value = True
        mock_get_service.return_value = mock_calendar_service
        
        # 1. Identifica tipo de paciente
        patient_type = setup_services['orchestrator'].identify_patient_type("Particular")
        assert patient_type == "private"
        
        # 2. Verifica disponibilidade e cria agendamento
        start_time = datetime.strptime(f"{test_data['appointment_date']} {test_data['appointment_time']}", "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=1)
        
        event = create_calendar_event(
            start_time,
            end_time,
            test_data['patient_name'],
            test_data['patient_phone'],
            "Consulta Particular"
        )
        
        assert event is not None
        assert 'id' in event
        assert event['id'] == 'test_event_id'
        
        # 3. Envia confirmação
        confirmation_message = f"Agendamento particular confirmado para {test_data['appointment_date']} às {test_data['appointment_time']}"
        setup_services['whatsapp_service'].send_message(test_data['patient_phone'], confirmation_message)
        
        # Verifica se a mensagem foi enviada
        mock_send_message.assert_called_with(test_data['patient_phone'], confirmation_message)
    
    @patch('app.services.whatsapp_service.WhatsAppService.send_message')
    @patch('app.services.calendar_service.get_calendar_service')
    def test_invalid_time_slot(
        self, mock_get_service, mock_send_message,
        setup_services, test_data, mock_calendar_slots, mock_calendar_service
    ):
        """Testa tentativa de agendamento em horário indisponível."""
        # Configura mock para lançar erro em horário inválido
        def mock_insert(*args, **kwargs):
            raise ValueError("Horário fora do expediente (9h às 17h)")
        
        mock_events = mock_calendar_service.events.return_value
        mock_events.insert.side_effect = mock_insert
        mock_get_service.return_value = mock_calendar_service
        mock_send_message.return_value = True
        
        # 1. Tenta criar agendamento em horário inválido
        invalid_time = "08:00"  # Horário fora do expediente
        start_time = datetime.strptime(f"{test_data['appointment_date']} {invalid_time}", "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(hours=1)
        
        with pytest.raises(ValueError):
            create_calendar_event(
                start_time,
                end_time,
                test_data['patient_name'],
                test_data['patient_phone'],
                "Consulta"
            )
        
        # 2. Verifica mensagem de erro
        error_message = "Desculpe, este horário não está disponível. Por favor, escolha outro horário."
        setup_services['whatsapp_service'].send_message(test_data['patient_phone'], error_message)
        
        # Verifica se a mensagem de erro foi enviada
        mock_send_message.assert_called_with(test_data['patient_phone'], error_message) 