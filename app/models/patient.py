from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class ConversationState(str, Enum):
    """Estados possíveis da conversa com o paciente."""
    INITIAL = "initial"
    COLLECTING_INFO = "collecting_info"
    VALIDATING_INSURANCE = "validating_insurance"
    SCHEDULING = "scheduling"
    CONFIRMING = "confirming"
    FINISHED = "finished"

class PatientType(str, Enum):
    """Tipos de paciente baseado na forma de pagamento."""
    PRIVATE = "private"
    INSURANCE = "insurance"
    UNDEFINED = "undefined"

class Patient(BaseModel):
    """Modelo de paciente com gerenciamento de estado."""
    id: str
    name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    patient_type: PatientType = PatientType.UNDEFINED
    insurance_id: Optional[str] = None
    insurance_card_number: Optional[str] = None
    
    # Campos de estado
    conversation_state: ConversationState = ConversationState.INITIAL
    last_interaction: Optional[datetime] = None
    context: Dict = {}  # Armazena informações temporárias da conversa
    appointment_history: List[datetime] = []

    def update_state(self, new_state: ConversationState) -> None:
        """Atualiza o estado da conversa."""
        self.conversation_state = new_state
        self.last_interaction = datetime.now()

    def add_context(self, key: str, value: any) -> None:
        """Adiciona informação ao contexto da conversa."""
        self.context[key] = value

    def clear_context(self) -> None:
        """Limpa o contexto da conversa."""
        self.context = {}

    def add_appointment(self, appointment_date: datetime) -> None:
        """Adiciona uma consulta ao histórico."""
        self.appointment_history.append(appointment_date)

    def get_last_appointment(self) -> Optional[datetime]:
        """Retorna a data da última consulta."""
        return self.appointment_history[-1] if self.appointment_history else None 