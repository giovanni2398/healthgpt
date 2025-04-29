import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import os
import json
import sqlite3

from app.main import app
from app.services.slot_management_service import SlotManagementService

client = TestClient(app)

# Configurar um banco de dados temporário para os testes
TEST_DB_PATH = "test_api_slots.db"


@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup - ensure fresh test database
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass  # Ignore if file is locked
    
    # Patch the get_slot_service dependency to use test database
    original_get_slot_service = app.dependency_overrides.copy()
    
    def get_test_slot_service():
        return SlotManagementService(db_path=TEST_DB_PATH)
    
    from app.api.slots import get_slot_service
    app.dependency_overrides[get_slot_service] = get_test_slot_service
    
    yield
    
    # Teardown - restore original dependencies and clean up
    app.dependency_overrides = original_get_slot_service
    
    # Wait a bit to ensure connections are closed
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass  # Ignore if file is locked


def test_generate_slots_api():
    """Test generating slots via API."""
    # Get tomorrow as start date to avoid any past date issues
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    
    request_data = {
        "start_date": tomorrow.isoformat(),
        "weeks_ahead": 1,
        "slot_duration_minutes": 30,
        "daily_start_hour": 9,
        "daily_end_hour": 17,
        "exclude_weekends": True
    }
    
    response = client.post("/slots/generate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "slots_generated" in data
    
    # Calculate expected number of slots for a week
    # 8 hours per day, 16 slots per day, 5 weekdays
    assert data["slots_generated"] > 0


def test_get_available_slots_api():
    """Test getting available slots via API."""
    # Generate some slots first
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    # Format dates for API request
    start_date_str = today.isoformat()
    end_date_str = (today + timedelta(days=7)).isoformat()
    
    request_data = {
        "start_date": start_date_str,
        "weeks_ahead": 1,
        "slot_duration_minutes": 30,
        "daily_start_hour": 9,
        "daily_end_hour": 17,
        "exclude_weekends": False  # Include all days to ensure we have slots
    }
    
    # Generate slots
    client.post("/slots/generate", json=request_data)
    
    # Get available slots
    response = client.get(
        f"/slots/available?start_date={start_date_str}&end_date={end_date_str}"
    )
    
    assert response.status_code == 200
    slots = response.json()
    assert isinstance(slots, list)
    assert len(slots) > 0
    
    # Verify slot structure
    first_slot = slots[0]
    assert "id" in first_slot
    assert "start_time" in first_slot
    assert "end_time" in first_slot
    assert "is_available" in first_slot
    assert first_slot["is_available"] is True


def test_book_slot_api():
    """Test booking a slot via API."""
    # Generate some slots first
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    request_data = {
        "start_date": today.isoformat(),
        "weeks_ahead": 1,
        "slot_duration_minutes": 30,
        "daily_start_hour": 9,
        "daily_end_hour": 17,
        "exclude_weekends": False
    }
    
    # Generate slots
    client.post("/slots/generate", json=request_data)
    
    # Get available slots
    response = client.get(
        f"/slots/available?start_date={today.isoformat()}&end_date={(today + timedelta(days=7)).isoformat()}"
    )
    
    assert response.status_code == 200
    slots = response.json()
    assert len(slots) > 0
    
    # Book the first slot
    slot_id = slots[0]["id"]
    book_data = {
        "appointment_id": "test-appointment-123"
    }
    
    response = client.post(f"/slots/{slot_id}/book", json=book_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # Verify slot is no longer available
    response = client.get(
        f"/slots/available?start_date={today.isoformat()}&end_date={(today + timedelta(days=7)).isoformat()}"
    )
    
    available_slots = response.json()
    slot_ids = [slot["id"] for slot in available_slots]
    assert slot_id not in slot_ids


def test_book_nonexistent_slot_api():
    """Test booking a slot that doesn't exist."""
    book_data = {
        "appointment_id": "test-appointment-456"
    }
    
    response = client.post("/slots/nonexistent-id/book", json=book_data)
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_cleanup_slots_api():
    """Test cleaning up old slots via API."""
    # Create past and future slots
    service = SlotManagementService(db_path=TEST_DB_PATH)
    
    # Insert past slots directly into the database
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)  # Adicionando a definição de tomorrow
    
    # Initialize database and ensure it exists
    service._init_db()
    
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Insert 5 past slots
        for i in range(5):
            start_time = yesterday + timedelta(hours=i)
            end_time = start_time + timedelta(minutes=30)
            cursor.execute(
                """
                INSERT INTO slots (id, start_time, end_time, is_available, appointment_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    f"past-slot-{i}",
                    start_time.isoformat(),
                    end_time.isoformat(),
                    1,
                    None
                )
            )
        
        # Insert 5 future slots (tomorrow)
        for i in range(5):
            start_time = tomorrow + timedelta(hours=i)
            end_time = start_time + timedelta(minutes=30)
            cursor.execute(
                """
                INSERT INTO slots (id, start_time, end_time, is_available, appointment_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    f"future-slot-{i}",
                    start_time.isoformat(),
                    end_time.isoformat(),
                    1,
                    None
                )
            )
        
        conn.commit()
        
        # Verify we have 10 slots total
        cursor.execute("SELECT COUNT(*) FROM slots")
        count = cursor.fetchone()[0]
        assert count == 10
    finally:
        # Ensure connection is closed
        conn.close()
    
    # Generate some future slots
    request_data = {
        "start_date": (now + timedelta(days=1)).isoformat(),
        "weeks_ahead": 1,
        "slot_duration_minutes": 30,
        "daily_start_hour": 9,
        "daily_end_hour": 12,
        "exclude_weekends": False
    }
    
    client.post("/slots/generate", json=request_data)
    
    # Cleanup old slots
    response = client.post("/slots/cleanup")
    
    assert response.status_code == 200
    data = response.json()
    assert data["slots_removed"] == 5  # Should remove the 5 past slots 