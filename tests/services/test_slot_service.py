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


def test_generate_slots_single_day(slot_service):
    """Test generating slots for a single day."""
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1) - timedelta(microseconds=1)  # End of the day
    slot_duration = timedelta(hours=1)
    
    # Exclude the current day of the week to ensure no slots are generated if it's a weekend
    current_weekday = start_date.weekday()
    excluded_days = [current_weekday]
    
    # Generate slots with custom times (10 AM to 2 PM) - should create 4 slots
    daily_start = timedelta(hours=10)
    daily_end = timedelta(hours=14)
    
    # First test - no slots on excluded day
    slot_ids = slot_service.generate_slots(
        start_date, end_date, slot_duration, 
        daily_start_time=daily_start, 
        daily_end_time=daily_end,
        excluded_days=excluded_days
    )
    assert len(slot_ids) == 0
    
    # Second test - include this day, should have 4 slots
    slot_ids = slot_service.generate_slots(
        start_date, end_date, slot_duration, 
        daily_start_time=daily_start, 
        daily_end_time=daily_end,
        excluded_days=[]
    )
    assert len(slot_ids) == 4
    
    # Verify all slots are one hour apart
    slots = [slot_service.get_slot(slot_id) for slot_id in slot_ids]
    slots.sort(key=lambda s: s["start_time"])
    
    for i in range(len(slots)):
        slot = slots[i]
        expected_start = start_date + daily_start + (i * slot_duration)
        expected_end = expected_start + slot_duration
        assert slot["start_time"] == expected_start
        assert slot["end_time"] == expected_end
        assert slot["is_available"] is True


def test_generate_slots_multiple_days(slot_service):
    """Test generating slots across multiple days."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = today
    end_date = today + timedelta(days=6)  # One week
    slot_duration = timedelta(minutes=30)
    
    # Custom schedule - 9 AM to 12 PM
    daily_start = timedelta(hours=9)
    daily_end = timedelta(hours=12)
    
    # Exclude weekends (Saturday=5, Sunday=6)
    excluded_days = [5, 6]
    
    slot_ids = slot_service.generate_slots(
        start_date, end_date, slot_duration, 
        daily_start_time=daily_start, 
        daily_end_time=daily_end,
        excluded_days=excluded_days
    )
    
    # Calculate expected number of slots:
    # - 3 hours per day (9 AM to 12 PM)
    # - 6 slots per day (30-minute slots)
    # - 5 weekdays in a week
    
    # Count working days in the date range
    working_days = 0
    current = start_date
    while current <= end_date:
        if current.weekday() not in excluded_days:
            working_days += 1
        current += timedelta(days=1)
    
    expected_slots = working_days * 6  # 6 slots per day
    assert len(slot_ids) == expected_slots
    
    # Verify all slots are correctly spaced
    all_slots = [slot_service.get_slot(slot_id) for slot_id in slot_ids]
    
    # Group slots by day
    slots_by_day = {}
    for slot in all_slots:
        day = slot["start_time"].date()
        if day not in slots_by_day:
            slots_by_day[day] = []
        slots_by_day[day].append(slot)
    
    # Verify each day has the correct number of slots
    for day, day_slots in slots_by_day.items():
        assert len(day_slots) == 6  # 6 slots per day
        
        # Sort slots by start time
        day_slots.sort(key=lambda s: s["start_time"])
        
        # Verify slot timings
        for i, slot in enumerate(day_slots):
            day_start = datetime.combine(day, datetime.min.time()) + daily_start
            expected_start = day_start + (i * slot_duration)
            expected_end = expected_start + slot_duration
            assert slot["start_time"] == expected_start
            assert slot["end_time"] == expected_end


def test_generate_slots_invalid_params(slot_service):
    """Test generating slots with invalid parameters."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Test invalid date range
    with pytest.raises(ValueError):
        slot_service.generate_slots(
            today + timedelta(days=1),  # Start date after end date
            today,
            timedelta(hours=1)
        )
    
    # Test invalid daily times
    with pytest.raises(ValueError):
        slot_service.generate_slots(
            today,
            today + timedelta(days=1),
            timedelta(hours=1),
            daily_start_time=timedelta(hours=17),  # Start time after end time
            daily_end_time=timedelta(hours=9)
        )
    
    # Test invalid slot duration
    with pytest.raises(ValueError):
        slot_service.generate_slots(
            today,
            today + timedelta(days=1),
            timedelta(hours=-1)  # Negative duration
        )


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