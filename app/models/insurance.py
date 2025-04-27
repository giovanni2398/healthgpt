from typing import Optional
from pydantic import BaseModel

class InsurancePlan(BaseModel):
    """Modelo simplificado para planos de convênio médico."""
    id: str
    name: str

class InsuranceValidation(BaseModel):
    """Modelo para registro do convênio e documentos do paciente."""
    insurance_id: str
    patient_id: str
    documents_received: bool = False  # Indica se os documentos foram recebidos

    def is_valid(self) -> bool:
        """Verifica se o convênio está válido."""
        return self.status == "active" and self.valid_until > datetime.now()

    def get_validation_message(self) -> str:
        """Retorna mensagem explicativa sobre o status do convênio."""
        if self.status == "inactive":
            return "Convênio inativo"
        if self.valid_until < datetime.now():
            return "Convênio vencido"
        return "Convênio válido"

    def is_valid_for_scheduling(self) -> bool:
        """Verifica se o convênio está válido para agendamento."""
        return self.documents_received 