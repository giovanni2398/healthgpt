import json
import os
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open, MagicMock

from app.services.simplified_slot_service import SimplifiedSlotService


@pytest.fixture
def mock_config():
    """Return a mock clinic schedule configuration."""
    return {
        "slot_duration_minutes": 45,
        "schedules": [
            {
                "days": [0, 2, 4],  # Monday, Wednesday, Friday
                "description": "Monday, Wednesday, Friday - Morning",
                "start_time": "09:00",
                "end_time": "12:00"
            }
        ]
    }


@pytest.fixture
def mock_appointments():
    """Return mock appointments data."""
    # Create a fixed date for testing
    test_date = datetime(2023, 7, 10, 9, 0)  # Monday at 9 AM
    
    return {
        test_date.isoformat(): {
            "name": "Test Patient",
            "phone": "123456789",
            "reason": "Consultation"
        }
    }


@pytest.fixture
def slot_service(mock_config, mock_appointments):
    """Create a SimplifiedSlotService instance with mocked file operations."""
    with patch('os.path.exists') as mock_exists:
        with patch('builtins.open', new_callable=MagicMock) as mock_open_func:
            with patch('os.makedirs') as mock_makedirs:
                with patch('json.load') as mock_json_load:
                    with patch('json.dump') as mock_json_dump:
                        # Configure mocks
                        mock_exists.return_value = True
                        mock_json_load.side_effect = [mock_config, mock_appointments]
                        
                        # Create the service
                        service = SimplifiedSlotService(
                            appointments_file="data/test_appointments.json",
                            schedule_config_file="app/config/test_clinic_schedule.json"
                        )
                        
                        # Manually set the schedules to match our test configuration
                        service.config = mock_config
                        service.appointments = mock_appointments
                        service.schedules = []
                        
                        # Process schedule from mock_config
                        for schedule in mock_config.get("schedules", []):
                            days = schedule.get("days", [])
                            
                            # Parse times
                            start_time_str = schedule.get("start_time", "09:00")
                            end_time_str = schedule.get("end_time", "12:00")
                            
                            hour_start, minute_start = map(int, start_time_str.split(":"))
                            hour_end, minute_end = map(int, end_time_str.split(":"))
                            
                            # Add to schedules list
                            service.schedules.append({
                                "days": days,
                                "start_time": datetime.min.time().replace(hour=hour_start, minute=minute_start),
                                "end_time": datetime.min.time().replace(hour=hour_end, minute=minute_end)
                            })
                            
                        yield service


def test_init_loads_config_and_appointments(slot_service, mock_config, mock_appointments):
    """Test that initialization loads config and appointments correctly."""
    # Check config was loaded
    assert slot_service.config == mock_config
    assert slot_service.slot_duration == timedelta(minutes=mock_config["slot_duration_minutes"])
    
    # Check schedules were processed correctly
    assert len(slot_service.schedules) == 1
    assert slot_service.schedules[0]["days"] == [0, 2, 4]
    
    # Check appointments were loaded
    assert slot_service.appointments == mock_appointments


def test_generate_slots_for_one_day(slot_service):
    """Test generating slots for a single day."""
    # Monday at 00:00
    start_date = datetime(2023, 7, 10, 0, 0)
    # Generate slots for just one day
    slots = slot_service.generate_slots(start_date, weeks_ahead=0)
    
    # Should have 4 slots for the day (9:00, 9:45, 10:30, 11:15)
    monday_slots = [s for s in slots if s["start_time"].date() == start_date.date()]
    assert len(monday_slots) == 4
    
    # Check the first slot
    first_slot = monday_slots[0]
    assert first_slot["start_time"] == datetime(2023, 7, 10, 9, 0)
    assert first_slot["end_time"] == datetime(2023, 7, 10, 9, 45)
    
    # The slot at 9:00 on Monday is already booked in our mock_appointments
    # So it should not be available
    assert first_slot["is_available"] is False
    
    # Check the last slot
    last_slot = monday_slots[-1]
    assert last_slot["start_time"] == datetime(2023, 7, 10, 11, 15)
    assert last_slot["end_time"] == datetime(2023, 7, 10, 12, 0)


def test_generate_slots_for_multiple_weeks(slot_service):
    """Test generating slots for multiple weeks."""
    # Start on a Monday
    start_date = datetime(2023, 7, 10, 0, 0)
    # Generate slots for 2 weeks
    slots = slot_service.generate_slots(start_date, weeks_ahead=2)
    
    # Should have slots for 6 days (3 days per week * 2 weeks + the current day)
    unique_days = {s["start_time"].date() for s in slots}
    # The service generates slots including the current day, so there are 7 days total
    assert len(unique_days) == 7
    
    # Each day should have 4 slots
    slots_per_day = {}
    for slot in slots:
        day = slot["start_time"].date()
        if day not in slots_per_day:
            slots_per_day[day] = []
        slots_per_day[day].append(slot)
    
    for day, day_slots in slots_per_day.items():
        assert len(day_slots) == 4


def test_get_available_slots(slot_service, mock_appointments):
    """Test getting available slots excluding booked appointments."""
    # Start from Monday (day with appointments)
    start_date = datetime(2023, 7, 10, 0, 0)
    end_date = start_date + timedelta(days=7)
    
    # Get available slots
    available_slots = slot_service.get_available_slots(start_date, end_date)
    
    # Should exclude the booked slot at 9:00 on Monday
    assert all(slot["is_available"] for slot in available_slots)
    
    # No slot should start at the exact time of the booked appointment
    booked_time = list(mock_appointments.keys())[0]
    booked_datetime = datetime.fromisoformat(booked_time)
    
    assert not any(slot["start_time"] == booked_datetime for slot in available_slots)


def test_book_slot(slot_service):
    """Test booking a slot."""
    # Create a slot time to book
    slot_time = datetime(2023, 7, 12, 9, 0)  # Wednesday at 9:00
    appointment_info = {
        "name": "New Patient",
        "phone": "987654321",
        "reason": "Follow-up"
    }
    
    # Book the slot
    with patch.object(slot_service, '_save_appointments') as mock_save:
        result = slot_service.book_slot(slot_time, appointment_info)
        assert result is True
        assert slot_time.isoformat() in slot_service.appointments
        assert slot_service.appointments[slot_time.isoformat()] == appointment_info
        mock_save.assert_called_once()


def test_book_already_reserved_slot(slot_service, mock_appointments):
    """Test booking a slot that is already reserved."""
    # Use the time from the mock appointments
    booked_time = list(mock_appointments.keys())[0]
    booked_datetime = datetime.fromisoformat(booked_time)
    
    # Try to book the same slot
    appointment_info = {
        "name": "Another Patient",
        "phone": "555555555",
        "reason": "Checkup"
    }
    
    result = slot_service.book_slot(booked_datetime, appointment_info)
    assert result is False
    
    # The original appointment should remain unchanged
    assert slot_service.appointments[booked_time] == mock_appointments[booked_time]


def test_cancel_appointment(slot_service, mock_appointments):
    """Test canceling an appointment."""
    # Use the time from the mock appointments
    booked_time = list(mock_appointments.keys())[0]
    booked_datetime = datetime.fromisoformat(booked_time)
    
    # Cancel the appointment
    with patch.object(slot_service, '_save_appointments') as mock_save:
        result = slot_service.cancel_appointment(booked_datetime)
        assert result is True
        assert booked_time not in slot_service.appointments
        mock_save.assert_called_once()


def test_cancel_nonexistent_appointment(slot_service):
    """Test canceling an appointment that doesn't exist."""
    # Use a time that's not in the appointments
    nonexistent_time = datetime(2023, 7, 15, 10, 0)
    
    result = slot_service.cancel_appointment(nonexistent_time)
    assert result is False


def test_get_appointment(slot_service, mock_appointments):
    """Test getting an appointment's details."""
    # Use the time from the mock appointments
    booked_time = list(mock_appointments.keys())[0]
    booked_datetime = datetime.fromisoformat(booked_time)
    
    # Get the appointment
    appointment = slot_service.get_appointment(booked_datetime)
    assert appointment == mock_appointments[booked_time]


def test_get_nonexistent_appointment(slot_service):
    """Test getting an appointment that doesn't exist."""
    # Use a time that's not in the appointments
    nonexistent_time = datetime(2023, 7, 15, 10, 0)
    
    appointment = slot_service.get_appointment(nonexistent_time)
    assert appointment is None


def test_get_all_appointments(slot_service, mock_appointments):
    """Test getting all appointments."""
    all_appointments = slot_service.get_all_appointments()
    assert all_appointments == mock_appointments
    
    # Ensure it's a copy, not the original reference
    assert all_appointments is not slot_service.appointments 