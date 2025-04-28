from datetime import datetime
from typing import List, Optional, Dict
from uuid import uuid4

from app.models.appointment import Appointment
from app.models.slot import TimeSlot
from app.services.slot_service import SlotService

class SchedulingService:
    """Serviço para gerenciar agendamentos."""
    
    def __init__(self, slot_service: SlotService = None):
        self.slot_service = slot_service or SlotService()
        self.appointments: List[Appointment] = []
    
    def create_appointment(
        self,
        patient_id: str,
        patient_name: str,
        slot_id: str,
        reason: str,
        is_private: bool = True,
        insurance: str = None,
        insurance_card_url: str = None,
        id_document_url: str = None
    ) -> Appointment:
        """
        Cria um novo agendamento, reservando o slot.
        """
        # Busca o slot e verifica disponibilidade
        slot = self.slot_service.get_slot(slot_id)
        if slot is None or not slot.get("is_available", False):
            raise ValueError("Horário não está mais disponível")

        # Cria o agendamento
        appointment = Appointment(
            id=str(uuid4()),
            patient_id=patient_id,
            name=patient_name,
            start_time=slot["start_time"],
            end_time=slot["end_time"],
            reason=reason,
            is_private=is_private,
            insurance=insurance,
            insurance_card_url=insurance_card_url,
            id_document_url=id_document_url,
            status="scheduled"
        )

        # Salva o agendamento
        self.appointments.append(appointment)

        # Marca o slot como reservado
        self.slot_service.reserve_slot(slot_id)

        return appointment
    
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
    
    def cancel_appointment(self, slot_id: str) -> bool:
        """Cancela um agendamento."""
        return self.slot_service.free_slot(slot_id)
    
    def get_available_slots(self, start_range: datetime, end_range: datetime) -> List[Dict]:
        """Retorna os slots disponíveis para agendamento."""
        return self.slot_service.get_available_slots(start_range, end_range)

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

    def create_appointment_slot(self, start_time: datetime, end_time: datetime) -> str:
        """Creates a new appointment slot."""
        return self.slot_service.create_slot(start_time, end_time)
    
    def schedule_appointment(self, slot_id: str) -> bool:
        """Schedules an appointment in the specified slot."""
        return self.slot_service.reserve_slot(slot_id)
    
    def get_slot(self, slot_id: str) -> Optional[Dict]:
        """Gets a specific slot by its ID."""
        return self.slot_service.get_slot(slot_id) 