import pytest
from datetime import datetime, timedelta
from types import SimpleNamespace

from app.services.calendar_service import validate_date, get_available_slots, create_calendar_event, SERVICE_ACCOUNT_FILE, CALENDAR_ID, SCOPES, get_calendar_service


def test_validate_date_success():
    # Deve aceitar datas no formato ISO 8601
    validate_date("2025-01-01")  # não deve lançar


def test_validate_date_error():
    with pytest.raises(ValueError) as excinfo:
        validate_date("2025-01-32")
    assert str(excinfo.value) == "Data inválida fornecida."


def test_get_available_slots_filters_events(monkeypatch):
    # Define data de teste
    date_str = "2025-02-01"
    # Cria um evento ocupando o slot das 12h às 13h
    event = {
        'start': {'dateTime': f"{date_str}T12:00:00"},
        'end': {'dateTime': f"{date_str}T13:00:00"}
    }
    # Fake service que retorna esse evento
    class FakeEvents:
        def list(self, **kwargs):
            return SimpleNamespace(execute=lambda: {'items': [event]})

    class FakeService:
        def events(self):
            return FakeEvents()

    # Monkeypatch do get_calendar_service
    monkeypatch.setattr(
        'app.services.calendar_service.get_calendar_service',
        lambda: FakeService()
    )

    slots = get_available_slots(date_str)
    # Há slots de 9 a 17h => 9 horários, mas 12h deve estar ocupado => 8 disponíveis
    assert isinstance(slots, list)
    assert len(slots) == 8
    # Verifica que não há slot em 12h
    times = [slot.hour for slot in slots]
    assert 12 not in times


def test_create_calendar_event_success(monkeypatch):
    # Prepara ambiente
    start = datetime(2025, 3, 1, 9, 0)
    end = datetime(2025, 3, 1, 10, 0)
    name = "Teste"
    phone = "+5511999999999"
    reason = "Motivo"
    # Fake retorno do insert
    returned_event = {'id': 'evt123', 'htmlLink': 'link123'}
    class FakeEventsInsert:
        def insert(self, calendarId, body):
            # Verifica parâmetros enviados
            assert calendarId == CALENDAR_ID
            assert 'summary' in body and name in body['summary']
            return SimpleNamespace(execute=lambda: returned_event)
    class FakeService2:
        def events(self):
            return FakeEventsInsert()
    # Monkeypatch do get_calendar_service
    monkeypatch.setattr(
        'app.services.calendar_service.get_calendar_service',
        lambda: FakeService2()
    )
    # Chama a criação
    event = create_calendar_event(start, end, name, phone, reason)
    assert event == returned_event 