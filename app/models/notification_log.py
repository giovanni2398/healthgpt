from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NotificationLog(BaseModel):
    """
    Modelo para armazenar logs de notificações enviadas.
    """
    id: str
    patient_name: str
    appointment_date: datetime
    notification_type: str = "appointment_reminder"
    message: str
    sent_at: datetime
    sent_by: str
    status: str = "pending"  # pending, sent, failed
    notes: Optional[str] = None 