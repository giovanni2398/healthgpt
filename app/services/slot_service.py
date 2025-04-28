from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

from app.models.slot import TimeSlot

class SlotService:
    """Serviço para gerenciar slots de horário disponíveis."""
    
    def __init__(self):
        self.slots: Dict[str, Dict] = {}
    
    def create_slot(self, start_time: datetime, end_time: datetime) -> str:
        """Creates a new time slot and returns its ID."""
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
        
        slot_id = str(uuid.uuid4())
        self.slots[slot_id] = {
            "id": slot_id,
            "start_time": start_time,
            "end_time": end_time,
            "is_available": True,
            "appointment_id": None
        }
        return slot_id
    
    def get_slot(self, slot_id: str) -> Optional[Dict]:
        """Gets a slot by its ID."""
        return self.slots.get(slot_id)
    
    def get_available_slots(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Gets all available slots within a date range."""
        available_slots = []
        for slot_id, slot in self.slots.items():
            if (slot["is_available"] and 
                slot["start_time"] >= start_date and 
                slot["end_time"] <= end_date):
                available_slots.append(slot)
        return available_slots
    
    def reserve_slot(self, slot_id: str) -> bool:
        """Marks a slot as reserved/unavailable."""
        if slot_id not in self.slots:
            return False
        if not self.slots[slot_id]["is_available"]:
            return False
        self.slots[slot_id]["is_available"] = False
        return True
    
    def free_slot(self, slot_id: str) -> bool:
        """Marks a slot as free/available."""
        if slot_id not in self.slots:
            return False
        self.slots[slot_id]["is_available"] = True
        self.slots[slot_id]["appointment_id"] = None
        return True
    
    def book_slot(self, slot_id: str, appointment_id: str) -> bool:
        """Books a slot for a specific appointment."""
        if slot_id not in self.slots:
            return False
        if not self.slots[slot_id]["is_available"]:
            return False
        self.slots[slot_id]["is_available"] = False
        self.slots[slot_id]["appointment_id"] = appointment_id
        return True 