from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from app.models.appointment import Appointment
from app.models.slot import TimeSlot
from app.services.slot_service import SlotService

class SchedulingService:
    """Serviço para gerenciar agendamentos."""
    
    def __init__(self):
        self.slot_service = SlotService()
        self.appointments: List[Appointment] = []
    
    def create_appointment(
        self,
        patient_id: str,
        patient_name: str,
        slot_id: str,
        reason: str,
        is_private: bool = True,
        insurance: Optional[str] = None,
        insurance_card_url: Optional[str] = None,
        id_document_url: Optional[str] = None
    ) -> Optional[Appointment]:
        """Cria um novo agendamento."""
        slot = self.slot_service.get_slot(slot_id)
        if not slot or not slot.is_available:
            return None
            
        appointment = Appointment(
            id=str(uuid4()),
            patient_id=patient_id,
            patient_name=patient_name,
            start_time=slot.start_time,
            end_time=slot.end_time,
            reason=reason,
            is_private=is_private,
            insurance=insurance,
            insurance_card_url=insurance_card_url,
            id_document_url=id_document_url
        )
        
        if self.slot_service.book_slot(slot_id, appointment.id):
            self.appointments.append(appointment)
            return appointment
        return None
    
    def get_appointment(self, appointment_id: str) -> Optional[Appointment]:
        """Retorna um agendamento pelo ID."""
        return next(
            (appointment for appointment in self.appointments 
             if appointment.id == appointment_id),
            None
        )
    
    def get_patient_appointments(
        self,
        patient_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Appointment]:
        """Retorna os agendamentos de um paciente dentro de um período."""
        appointments = [
            appointment for appointment in self.appointments
            if appointment.patient_id == patient_id
            and (start_date is None or appointment.start_time >= start_date)
            and (end_date is None or appointment.end_time <= end_date)
        ]
        return sorted(appointments, key=lambda x: x.start_time)
    
    def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancela um agendamento."""
        appointment = self.get_appointment(appointment_id)
        if appointment and appointment.status == "scheduled":
            appointment.status = "cancelled"
            self.slot_service.free_slot(appointment.slot_id)
            return True
        return False
    
    def get_available_slots(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[TimeSlot]:
        """Retorna os slots disponíveis para agendamento."""
        return self.slot_service.get_available_slots(start_date, end_date)

    def generate_available_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        interval_minutes: int = 30
    ) -> List[TimeSlot]:
        """Gera slots de horário disponíveis para um período."""
        return self.slot_service.generate_slots(
            start_date=start_date,
            end_date=end_date,
            interval_minutes=interval_minutes
        ) 