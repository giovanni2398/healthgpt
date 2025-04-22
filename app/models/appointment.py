from pydantic import BaseModel
from datetime import datetime

class Appointment(BaseModel):
    patient_name: str
    date: datetime
    method: str  # particular ou convênio
    insurance: str | None = None
