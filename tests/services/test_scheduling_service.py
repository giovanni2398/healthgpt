import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from app.services.scheduling_service import SchedulingService
from app.services.slot_service import SlotService

@pytest.fixture
def mock_slot_service():
    """Fixture that provides a mocked SlotService."""
    return MagicMock(spec=SlotService)

@pytest.fixture
def scheduling_service(mock_slot_service):
    """Fixture that provides a SchedulingService with mocked dependencies."""
    return SchedulingService(slot_service=mock_slot_service)

def test_create_appointment_slot(scheduling_service, mock_slot_service):
    """Test creating a new appointment slot."""
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=1)
    slot_id = "test-slot-id"
    
    mock_slot_service.create_slot.return_value = slot_id
    
    result = scheduling_service.create_appointment_slot(start_time, end_time)
    
    assert result == slot_id
    mock_slot_service.create_slot.assert_called_once_with(start_time, end_time)

def test_get_available_slots(scheduling_service, mock_slot_service):
    """Test getting available slots."""
    start_range = datetime.now()
    end_range = start_range + timedelta(days=1)
    mock_slots = [
        {"id": "slot1", "start_time": start_range, "end_time": start_range + timedelta(hours=1), "is_available": True},
        {"id": "slot2", "start_time": start_range + timedelta(hours=2), "end_time": start_range + timedelta(hours=3), "is_available": True}
    ]
    
    mock_slot_service.get_available_slots.return_value = mock_slots
    
    result = scheduling_service.get_available_slots(start_range, end_range)
    
    assert result == mock_slots
    mock_slot_service.get_available_slots.assert_called_once_with(start_range, end_range)

def test_schedule_appointment(scheduling_service, mock_slot_service):
    """Test scheduling an appointment."""
    slot_id = "test-slot-id"
    mock_slot_service.reserve_slot.return_value = True
    
    result = scheduling_service.schedule_appointment(slot_id)
    
    assert result is True
    mock_slot_service.reserve_slot.assert_called_once_with(slot_id)

def test_cancel_appointment(scheduling_service, mock_slot_service):
    """Test canceling an appointment."""
    slot_id = "test-slot-id"
    mock_slot_service.free_slot.return_value = True
    
    result = scheduling_service.cancel_appointment(slot_id)
    
    assert result is True
    mock_slot_service.free_slot.assert_called_once_with(slot_id)

def test_get_slot(scheduling_service, mock_slot_service):
    """Test getting a specific slot."""
    slot_id = "test-slot-id"
    mock_slot = {
        "id": slot_id,
        "start_time": datetime.now(),
        "end_time": datetime.now() + timedelta(hours=1),
        "is_available": True
    }
    
    mock_slot_service.get_slot.return_value = mock_slot
    
    result = scheduling_service.get_slot(slot_id)
    
    assert result == mock_slot
    mock_slot_service.get_slot.assert_called_once_with(slot_id) 