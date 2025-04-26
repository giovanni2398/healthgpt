from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class InsurancePlan(BaseModel):
    """Modelo para planos de convênio médico."""
    id: str
    name: str
    provider: str
    coverage_type: str  # basic, standard, premium
    waiting_period_days: int = 0
    active: bool = True

class InsuranceValidation(BaseModel):
    """Modelo para validação de convênio de um paciente."""
    insurance_id: str
    patient_id: str
    card_number: str
    valid_until: datetime
    status: str  # active, inactive, waiting_period
    waiting_period_ends: Optional[datetime] = None

    def is_valid(self) -> bool:
        """Verifica se o convênio está válido."""
        now = datetime.now()
        if not self.status == "active":
            return False
        if self.valid_until < now:
            return False
        if self.waiting_period_ends and self.waiting_period_ends > now:
            return False
        return True

    def get_validation_message(self) -> str:
        """Retorna mensagem explicativa sobre o status do convênio."""
        if self.status == "inactive":
            return "Convênio inativo"
        if self.valid_until < datetime.now():
            return "Convênio vencido"
        if self.waiting_period_ends and self.waiting_period_ends > datetime.now():
            return f"Em período de carência até {self.waiting_period_ends.strftime('%d/%m/%Y')}"
        return "Convênio válido" 