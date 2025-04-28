import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.slot_service import SlotService
from app.models.slot import TimeSlot


@pytest.fixture
def slot_service():
    """Pytest fixture para criar uma instância limpa de SlotService."""
    return SlotService()


def test_create_slot(slot_service: SlotService):
    """Testa a criação de um slot."""
    start = datetime(2025, 1, 1, 9, 0)
    end = datetime(2025, 1, 1, 9, 30)
    slot = slot_service.create_slot(start, end)
    assert isinstance(slot, TimeSlot)
    assert slot.start_time == start
    assert slot.end_time == end
    assert slot.is_available is True
    assert slot.appointment_id is None
    # Check if slot is added to the service's list
    assert slot in slot_service.slots


def test_get_slot(slot_service: SlotService):
    """Testa a busca de um slot pelo ID."""
    start = datetime(2025, 1, 1, 10, 0)
    end = datetime(2025, 1, 1, 10, 30)
    slot = slot_service.create_slot(start, end)
    fetched_slot = slot_service.get_slot(slot.id)
    assert fetched_slot == slot
    # Test getting a non-existent slot
    assert slot_service.get_slot("non-existent-id") is None


def test_get_available_slots(slot_service: SlotService):
    """Testa a busca de slots disponíveis em um período."""
    start_range = datetime(2025, 1, 2, 0, 0)
    end_range = datetime(2025, 1, 2, 12, 0)
    
    slot1 = slot_service.create_slot(datetime(2025, 1, 2, 9, 0), datetime(2025, 1, 2, 9, 30))
    slot2 = slot_service.create_slot(datetime(2025, 1, 2, 10, 0), datetime(2025, 1, 2, 10, 30))
    slot3 = slot_service.create_slot(datetime(2025, 1, 2, 11, 0), datetime(2025, 1, 2, 11, 30))
    slot_outside = slot_service.create_slot(datetime(2025, 1, 2, 13, 0), datetime(2025, 1, 2, 13, 30))
    
    # Make slot2 unavailable
    slot_service.book_slot(slot2.id, "appt123")
    
    available = slot_service.get_available_slots(start_range, end_range)
    assert isinstance(available, list)
    assert len(available) == 2
    assert slot1 in available
    assert slot3 in available
    assert slot2 not in available
    assert slot_outside not in available


def test_book_slot(slot_service: SlotService):
    """Testa a reserva (booking) de um slot."""
    start = datetime(2025, 1, 3, 14, 0)
    end = datetime(2025, 1, 3, 14, 30)
    slot = slot_service.create_slot(start, end)
    appointment_id = str(uuid4())
    
    # Book the slot
    success = slot_service.book_slot(slot.id, appointment_id)
    assert success is True
    assert slot.is_available is False
    assert slot.appointment_id == appointment_id
    
    # Try to book the same slot again
    assert slot_service.book_slot(slot.id, "another_appt") is False
    
    # Try to book a non-existent slot
    assert slot_service.book_slot("non-existent", "appt456") is False


def test_free_slot(slot_service: SlotService):
    """Testa a liberação de um slot."""
    start = datetime(2025, 1, 4, 15, 0)
    end = datetime(2025, 1, 4, 15, 30)
    slot = slot_service.create_slot(start, end)
    appointment_id = "appt789"
    
    # Book the slot first
    slot_service.book_slot(slot.id, appointment_id)
    assert not slot.is_available
    
    # Free the slot
    success = slot_service.free_slot(slot.id)
    assert success is True
    assert slot.is_available is True
    assert slot.appointment_id is None
    
    # Try to free an already available slot
    assert slot_service.free_slot(slot.id) is False
    
    # Try to free a non-existent slot
    assert slot_service.free_slot("non-existent") is False 