from datetime import datetime
from typing import Optional

class TimeSlot:
    """Modelo para representar um slot de horário disponível para agendamento."""
    
    def __init__(
        self,
        id: str,
        start_time: datetime,
        end_time: datetime,
        is_available: bool = True,
        appointment_id: Optional[str] = None
    ):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.is_available = is_available
        self.appointment_id = appointment_id

    def is_valid(self) -> bool:
        """Verifica se o slot é válido."""
        return (
            self.is_available and
            self.start_time > datetime.now() and
            self.end_time > self.start_time
        )

    def duration_minutes(self) -> int:
        """Calcula a duração do slot em minutos."""
        return int((self.end_time - self.start_time).total_seconds() / 60) 