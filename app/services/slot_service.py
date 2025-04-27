from datetime import datetime, timedelta
from typing import List, Optional
from uuid import uuid4

from app.models.slot import TimeSlot

class SlotService:
    """Serviço para gerenciar slots de horário disponíveis."""
    
    def __init__(self):
        self.slots: List[TimeSlot] = []
    
    def create_slot(self, start_time: datetime, end_time: datetime) -> TimeSlot:
        """Cria um novo slot de horário."""
        slot = TimeSlot(
            id=str(uuid4()),
            start_time=start_time,
            end_time=end_time
        )
        self.slots.append(slot)
        return slot
    
    def get_slot(self, slot_id: str) -> Optional[TimeSlot]:
        """Retorna um slot pelo ID."""
        return next((slot for slot in self.slots if slot.id == slot_id), None)
    
    def get_available_slots(self, start_date: datetime, end_date: datetime) -> List[TimeSlot]:
        """Retorna todos os slots disponíveis dentro do período especificado."""
        return [
            slot for slot in self.slots
            if slot.is_available
            and slot.start_time >= start_date
            and slot.end_time <= end_date
        ]
    
    def book_slot(self, slot_id: str, appointment_id: str) -> bool:
        """Marca um slot como ocupado por um agendamento."""
        slot = self.get_slot(slot_id)
        if slot and slot.is_available:
            slot.is_available = False
            slot.appointment_id = appointment_id
            return True
        return False
    
    def free_slot(self, slot_id: str) -> bool:
        """Libera um slot que estava ocupado."""
        slot = self.get_slot(slot_id)
        if slot and not slot.is_available:
            slot.is_available = True
            slot.appointment_id = None
            return True
        return False 