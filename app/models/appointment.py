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
