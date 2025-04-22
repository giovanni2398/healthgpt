from pydantic import BaseModel
from typing import List
from datetime import datetime

# Este modelo define como será a resposta com os horários disponíveis para agendamento
class AvailabilityResponse(BaseModel):
    available_slots: List[datetime]  # Lista de horários disponíveis (formato ISO 8601)
