import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.slot_service import SlotService


@pytest.fixture
def slot_service():
    """Create a new instance of SlotService for each test."""
    return SlotService()


def test_create_slot(slot_service):
    """Test creating a new slot with valid times."""
    start_time = datetime.now() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)

    slot_id = slot_service.create_slot(start_time, end_time)
    assert isinstance(slot_id, str)
    slot = slot_service.get_slot(slot_id)
    assert slot is not None
    assert slot["id"] == slot_id
    assert slot["start_time"] == start_time
    assert slot["end_time"] == end_time
    assert slot["is_available"] is True


def test_create_slot_invalid_times(slot_service):
    """Test creating a slot with invalid times (end before start)."""
    start_time = datetime.now() + timedelta(hours=2)
    end_time = start_time - timedelta(hours=1)

    with pytest.raises(ValueError):
        slot_service.create_slot(start_time, end_time)


def test_get_available_slots(slot_service):
    """Test getting available slots."""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)

    slot1_id = slot_service.create_slot(
        start_date + timedelta(hours=1),
        start_date + timedelta(hours=2)
    )
    slot2_id = slot_service.create_slot(
        start_date + timedelta(hours=3),
        start_date + timedelta(hours=4)
    )

    slot_service.reserve_slot(slot1_id)

    available_slots = slot_service.get_available_slots(start_date, end_date)
    assert len(available_slots) == 1
    assert available_slots[0]["id"] == slot2_id


def test_reserve_and_free_slot(slot_service):
    """Test reserving and freeing a slot."""
    start_time = datetime.now() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)

    slot_id = slot_service.create_slot(start_time, end_time)
    reserve_result = slot_service.reserve_slot(slot_id)
    assert reserve_result is True

    free_result = slot_service.free_slot(slot_id)
    assert free_result is True

    available_slots = slot_service.get_available_slots(start_time, end_time)
    assert len(available_slots) == 1
    assert available_slots[0]["id"] == slot_id


def test_reserve_nonexistent_slot(slot_service):
    """Test reserving a slot that doesn't exist."""
    result = slot_service.reserve_slot("nonexistent-id")
    assert result is False


def test_free_nonexistent_slot(slot_service):
    """Test freeing a slot that doesn't exist."""
    result = slot_service.free_slot("nonexistent-id")
    assert result is False


def test_book_slot(slot_service):
    """Test booking a slot with an appointment."""
    start_time = datetime.now() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)

    slot_id = slot_service.create_slot(start_time, end_time)

    appointment_id = "test-appointment-123"
    result = slot_service.book_slot(slot_id, appointment_id)
    assert result is True
    slot = slot_service.get_slot(slot_id)
    assert slot["appointment_id"] == appointment_id

    available_slots = slot_service.get_available_slots(start_time, end_time)
    assert len(available_slots) == 0 