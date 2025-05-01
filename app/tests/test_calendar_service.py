import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from app.services.calendar_service import CalendarService, CalendarEvent

@pytest.fixture
def mock_credentials():
    """Fixture para mock das credenciais do Google"""
    with patch('google.oauth2.credentials.Credentials') as mock:
        yield mock

@pytest.fixture
def mock_calendar_service():
    """Fixture para mock do serviço do Google Calendar"""
    with patch('app.services.calendar_service.CalendarService._authenticate') as mock_auth:
        service = CalendarService()
        service.service = MagicMock()
        yield service

def test_check_availability(mock_calendar_service):
    """Testa a verificação de disponibilidade no calendário"""
    service = mock_calendar_service
    
    # Configura o mock para retornar lista vazia de eventos (horário disponível)
    service.service.events().list().execute.return_value = {'items': []}
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)
    
    assert service.check_availability(start_time, end_time) == True
    
    # Configura o mock para retornar um evento (horário ocupado)
    service.service.events().list().execute.return_value = {
        'items': [{'start': {'dateTime': start_time.isoformat()}}]
    }
    
    assert service.check_availability(start_time, end_time) == False

def test_get_available_slots(mock_calendar_service):
    """Testa a obtenção de horários disponíveis"""
    service = mock_calendar_service
    
    # Configura o mock para retornar lista vazia de eventos
    service.service.events().list().execute.return_value = {'items': []}
    
    date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    slots = service.get_available_slots(date)
    
    # Verifica se retornou slots entre 9h e 18h
    assert len(slots) > 0
    assert all(9 <= slot.hour < 18 for slot in slots)
    assert all(slot.minute in (0, 30) for slot in slots)

def test_create_calendar_event(mock_calendar_service):
    """Testa a criação de eventos no calendário"""
    service = mock_calendar_service
    
    event = CalendarEvent(
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=1),
        patient_name="João Silva",
        patient_phone="11999999999",
        reason="Consulta de Nutrição",
        insurance="unimed"
    )
    
    # Testa criação bem sucedida
    service.service.events().insert().execute.return_value = {'id': '123'}
    assert service.create_calendar_event(event) == True
    
    # Testa erro na criação
    service.service.events().insert().execute.side_effect = Exception("API Error")
    assert service.create_calendar_event(event) == False

def test_cancel_appointment(mock_calendar_service):
    """Testa o cancelamento de agendamentos"""
    service = mock_calendar_service
    
    # Testa cancelamento bem sucedido
    assert service.cancel_appointment("123") == True
    
    # Testa erro no cancelamento
    service.service.events().delete().execute.side_effect = Exception("API Error")
    assert service.cancel_appointment("123") == False 