# test_calendar.py

import os
from dotenv import load_dotenv
from app.services.calendar_service import get_available_slots

load_dotenv()

def test_get_available_slots():
    date = "2025-04-23"  # Data com eventos no calendário
    slots = get_available_slots(date)
    print("Slots disponíveis:", slots)

if __name__ == "__main__":
    test_get_available_slots()

# testar a função get_available_slots
def test_calendar_slots():
    # Teste com uma data válida
    date = "2025-04-23"  # Data no formato ISO 8601 (AAAA-MM-DD)
    slots = get_available_slots(date)
    assert isinstance(slots, list), "A resposta deve ser uma lista."
    assert len(slots) > 0, "A lista de horários disponíveis não deve estar vazia."

    # Teste com uma data inválida
    invalid_date = "2025-04-31"  # Data inválida (31 de abril não existe)
    try:
        get_available_slots(invalid_date)
    except ValueError as e:
        assert str(e) == "Data inválida fornecida."

if __name__ == "__main__":
    test_calendar_slots()
  