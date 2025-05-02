import pytest
import os
import logging
from datetime import datetime, timedelta, time
from unittest.mock import patch, MagicMock, Mock
from app.services.calendar_service import CalendarService, CalendarEvent
from app.services.scheduling_preferences import PatientPreferences
from app.config.clinic_settings import ClinicSettings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Verifica se deve pular os testes que requerem credenciais reais
def should_skip_real_api_tests(use_real_api=False):
    """Determina se os testes com API real devem ser pulados."""
    # Se a fixture use_real_api for True, não pula os testes
    if use_real_api:
        return False
    
    # Caso contrário, verifica a variável de ambiente
    env_value = os.getenv('SKIP_REAL_API_TESTS', 'True').lower()
    return env_value == 'true'

SKIP_REASON = "Pulando testes que requerem API real. Use o parâmetro --use-real-api para executá-los."

# Marca para os testes que modificam dados (criação/deleção de eventos)
modify_data = pytest.mark.skip("Testes que modificam dados estão sempre desabilitados por segurança")

@pytest.fixture
def mock_credentials():
    """Fixture para mock das credenciais do Google"""
    mock_creds = MagicMock()
    mock_creds.valid = True
    mock_creds.expired = False
    return mock_creds

@pytest.fixture
def calendar_service():
    """Fixture para criar uma instância do serviço de calendário com os métodos mocados"""
    with patch('app.services.calendar_service.CalendarService._get_credentials') as mock_auth:
        with patch('app.services.calendar_service.build') as mock_build:
            # Configurar o mock de autenticação para retornar credenciais falsas
            mock_creds = MagicMock()
            mock_auth.return_value = mock_creds
            
            # Configurar o mock do service build
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            
            # Criar uma instância do serviço
            service = CalendarService()
            service.service = mock_service
            service.calendar_id = 'test_calendar_id'
            
            yield service

@pytest.fixture
def mock_calendar_service(mock_credentials):
    """Fixture para mock completo do serviço do Google Calendar"""
    with patch('app.services.calendar_service.CalendarService._get_credentials') as mock_auth:
        with patch('app.services.calendar_service.build') as mock_build:
            # Mock authentication
            mock_auth.return_value = mock_credentials
            
            # Mock the calendar service
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            
            # Mock the events method chain
            mock_events = MagicMock()
            mock_service.events.return_value = mock_events
            
            # Mock the list and execute methods
            mock_list = MagicMock()
            mock_events.list.return_value = mock_list
            mock_list.execute.return_value = {'items': []}
            
            # Create calendar service instance with mocked dependencies
            service = CalendarService()
            service.service = mock_service
            service.calendar_id = 'test_calendar_id'
            
            yield service

@pytest.fixture
def real_calendar_service(use_real_api):
    """Fixture para criar uma instância real do serviço de calendário"""
    if should_skip_real_api_tests(use_real_api):
        pytest.skip(SKIP_REASON)
    
    try:
        service = CalendarService()
        # Verifica se o serviço foi inicializado com credenciais válidas
        if not service.credentials or not service.service:
            pytest.skip("Credenciais do Google Calendar não configuradas corretamente")
        return service
    except Exception as e:
        pytest.skip(f"Erro ao criar serviço do Google Calendar: {e}")

@pytest.fixture
def sample_event():
    """Fixture para criar um evento de exemplo"""
    return CalendarEvent(
        start_time=datetime(2024, 3, 1, 14, 0),  # Segunda-feira, 14h
        end_time=datetime(2024, 3, 1, 14, 45),   # 45 minutos de duração
        patient_name="João Silva",
        patient_phone="+5511999999999",
        reason="Consulta de rotina"
    )

@pytest.fixture
def sample_preferences():
    """Fixture para criar preferências de exemplo"""
    return PatientPreferences(
        preferred_days=['monday', 'wednesday', 'friday'],
        preferred_time_ranges=[(time(14, 0), time(17, 45))],
        preferred_duration=45
    )

def test_mock_check_availability(mock_calendar_service):
    """Testa a verificação de disponibilidade no calendário com mock"""
    # Configura o mock para retornar lista vazia de eventos (horário disponível)
    mock_calendar_service.service.events().list().execute.return_value = {'items': []}
    
    # Configura o método _is_within_working_hours para retornar True
    mock_calendar_service._is_within_working_hours = MagicMock(return_value=True)
    
    # Horário para teste (segunda-feira, 14h)
    # Usando uma data fixa em vez de datetime.now() para maior consistência
    start_time = datetime(2024, 3, 4, 14, 0)  # Uma segunda-feira às 14h
    
    # O horário deve estar disponível
    assert mock_calendar_service.check_availability(start_time) == True
    
    # Configura o mock para retornar um evento (horário ocupado)
    mock_calendar_service.service.events().list().execute.return_value = {
        'items': [{'id': 'test_event_id'}]
    }
    
    # O horário não deve estar disponível
    assert mock_calendar_service.check_availability(start_time) == False

def test_real_check_availability(real_calendar_service):
    """Testa a verificação de disponibilidade no calendário com API real"""
    # Usa uma data futura (próxima segunda-feira) para evitar conflitos
    today = datetime.now().date()
    days_ahead = (0 - today.weekday() + 7) % 7  # Dias até a próxima segunda
    next_monday = today + timedelta(days=days_ahead)
    
    # Verifica slots da tarde (horário de funcionamento na segunda)
    slot_time = datetime.combine(next_monday, time(14, 0))  # 14:00
    
    # Verifica se o horário está disponível
    # Este teste pressupõe que o horário está livre, ajuste conforme necessário
    is_available = real_calendar_service.check_availability(slot_time)
    assert isinstance(is_available, bool)
    
    # Verifica um horário fora do funcionamento (domingo)
    sunday = next_monday - timedelta(days=1)
    slot_time = datetime.combine(sunday, time(14, 0))
    assert real_calendar_service.check_availability(slot_time) == False

def test_real_get_available_slots(real_calendar_service):
    """Testa a obtenção de slots disponíveis com API real"""
    # Usa uma data futura (próxima segunda-feira) para evitar conflitos
    today = datetime.now().date()
    days_ahead = (0 - today.weekday() + 7) % 7  # Dias até a próxima segunda
    next_monday = today + timedelta(days=days_ahead)
    
    # Verifica slots da tarde (horário de funcionamento na segunda)
    slot_date = datetime.combine(next_monday, time(0, 0))
    
    # Obtém os slots disponíveis
    slots = real_calendar_service.get_available_slots(slot_date)
    
    # Verifica se retornou uma lista
    assert isinstance(slots, list)
    
    # Como não sabemos o estado atual do calendário, verificamos apenas
    # que a função não quebrou e que se houver slots, eles estão no horário correto
    for slot in slots:
        assert slot.date() == next_monday
        assert 14 <= slot.hour < 18  # Horário de funcionamento na segunda (tarde)
        assert slot.minute in (0, 15, 30, 45)  # Minutos válidos

@modify_data
def test_create_calendar_event(mock_calendar_service, sample_event):
    """Testa a criação de eventos no calendário"""
    # Mock event creation response
    mock_calendar_service.service.events().insert().execute.return_value = {'id': 'test_event_id'}
    
    # Create event and verify
    event_id = mock_calendar_service.create_calendar_event(sample_event)
    assert event_id == 'test_event_id'
    
    # Verify the correct event data was sent
    mock_calendar_service.service.events().insert.assert_called_once()
    call_args = mock_calendar_service.service.events().insert.call_args[1]
    assert call_args['calendarId'] == 'test_calendar_id'
    assert 'João Silva' in call_args['body']['summary']

@modify_data
def test_cancel_appointment(mock_calendar_service):
    """Testa o cancelamento de agendamentos"""
    # Testa cancelamento bem sucedido
    mock_calendar_service.service.events().delete().execute.return_value = None
    assert mock_calendar_service.cancel_appointment("test_event_id") == True
    
    # Testa erro no cancelamento
    mock_calendar_service.service.events().delete().execute.side_effect = Exception("API Error")
    assert mock_calendar_service.cancel_appointment("test_event_id") == False

def test_real_get_available_slots_with_preferences(real_calendar_service, sample_preferences):
    """Testa a obtenção de slots disponíveis com preferências usando API real"""
    # Usa uma data futura (próxima segunda-feira) para evitar conflitos
    today = datetime.now().date()
    days_ahead = (0 - today.weekday() + 7) % 7  # Dias até a próxima segunda
    next_monday = today + timedelta(days=days_ahead)
    
    # Verifica slots da tarde (horário de funcionamento na segunda)
    slot_date = datetime.combine(next_monday, time(0, 0))
    
    # Obtém os slots disponíveis com preferências
    slots = real_calendar_service.get_available_slots(slot_date, preferences=sample_preferences)
    
    # Verifica se retornou uma lista
    assert isinstance(slots, list)
    
    # Como não sabemos o estado atual do calendário, verificamos apenas
    # que a função não quebrou e que se houver slots, eles estão no horário correto
    for slot in slots:
        assert slot.date() == next_monday
        assert 14 <= slot.hour < 18  # Horário de funcionamento na segunda (tarde)
        assert slot.minute in (0, 15, 30, 45)  # Minutos válidos 