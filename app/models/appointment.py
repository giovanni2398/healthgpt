from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Este modelo define os dados que o usuário deve fornecer ao pedir um agendamento
class AppointmentRequest(BaseModel):
    name: str  # Nome do paciente
    phone: str  # Telefone do paciente (pode ser usado como ID para WhatsApp)
    is_private: bool  # True se for atendimento particular, False se for convênio
    insurance: Optional[str] = None  # Nome do convênio, se houver
    preferred_date: Optional[str] = None  # Data preferida no formato 'YYYY-MM-DD'
    preferred_time: Optional[str] = None  # Horário preferido no formato 'HH:MM'

# Este modelo define a resposta que o sistema dá após tentar agendar a consulta
class AppointmentResponse(BaseModel):
    success: bool  # Indica se o agendamento foi feito com sucesso
    message: str  # Mensagem explicativa
    calendar_link: Optional[str] = None  # Link do evento no Google Calendar (se criado)
    confirmed_time: Optional[datetime] = None  # Horário real da consulta confirmada

class Appointment:
    """Modelo para representar um agendamento de consulta."""
    
    def __init__(
        self,
        id: str,
        patient_id: str,
        patient_name: str,
        start_time: datetime,
        end_time: datetime,
        reason: str,
        is_private: bool = True,
        insurance: Optional[str] = None,
        insurance_card_url: Optional[str] = None,
        id_document_url: Optional[str] = None,
        status: str = "scheduled"
    ):
        self.id = id
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.start_time = start_time
        self.end_time = end_time
        self.reason = reason
        self.is_private = is_private
        self.insurance = insurance
        self.insurance_card_url = insurance_card_url
        self.id_document_url = id_document_url
        self.status = status
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte o agendamento para um dicionário."""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "patient_name": self.patient_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "reason": self.reason,
            "is_private": self.is_private,
            "insurance": self.insurance,
            "insurance_card_url": self.insurance_card_url,
            "id_document_url": self.id_document_url,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
