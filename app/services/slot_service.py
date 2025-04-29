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
    
    def generate_slots(self, 
                       start_date: datetime, 
                       end_date: datetime, 
                       slot_duration: timedelta,
                       daily_start_time: timedelta = timedelta(hours=9),
                       daily_end_time: timedelta = timedelta(hours=17),
                       excluded_days: List[int] = None) -> List[str]:
        """
        Generates multiple slots between start_date and end_date with specified duration.
        
        Args:
            start_date: The starting date for slot generation
            end_date: The ending date for slot generation
            slot_duration: Duration of each slot
            daily_start_time: Time to start slots each day (default: 9:00 AM)
            daily_end_time: Time to end slots each day (default: 5:00 PM)
            excluded_days: List of days to exclude (0=Monday, 6=Sunday, default: weekends [5,6])
            
        Returns:
            List of generated slot IDs
        """
        if excluded_days is None:
            excluded_days = [5, 6]  # Saturday and Sunday by default
            
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
            
        if daily_start_time >= daily_end_time:
            raise ValueError("Daily start time must be before daily end time")
            
        if slot_duration <= timedelta(0):
            raise ValueError("Slot duration must be positive")
            
        generated_slot_ids = []
        current_date = start_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        while current_date <= end_date:
            # Skip excluded days
            if current_date.weekday() in excluded_days:
                current_date += timedelta(days=1)
                continue
                
            # Calculate the actual start and end times for this day
            day_start = current_date + daily_start_time
            day_end = current_date + daily_end_time
            
            # Generate slots for this day
            slot_start = day_start
            while slot_start + slot_duration <= day_end:
                slot_end = slot_start + slot_duration
                slot_id = self.create_slot(slot_start, slot_end)
                generated_slot_ids.append(slot_id)
                slot_start = slot_end
                
            current_date += timedelta(days=1)
            
        return generated_slot_ids
    
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