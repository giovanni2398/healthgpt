from typing import Dict, List, Optional
from ..models.insurance import InsurancePlan, InsuranceValidation
from ..config.insurance_plans import ACCEPTED_INSURANCE_PLANS

class InsuranceService:
    """Serviço para gerenciamento de convênios e documentos."""
    
    def __init__(self):
        self._accepted_plans = ACCEPTED_INSURANCE_PLANS
        self._validations: Dict[str, InsuranceValidation] = {}

    def get_accepted_plans(self) -> List[InsurancePlan]:
        """Retorna lista de planos aceitos."""
        return list(self._accepted_plans.values())

    def get_plan_by_name(self, plan_name: str) -> Optional[InsurancePlan]:
        """Busca um plano pelo nome (case insensitive)."""
        plan_name = plan_name.lower()
        for plan in self._accepted_plans.values():
            if plan.name.lower() == plan_name:
                return plan
        return None

    def register_insurance(
        self,
        patient_id: str,
        insurance_id: str
    ) -> InsuranceValidation:
        """
        Registra o convênio escolhido pelo paciente.
        """
        if insurance_id not in self._accepted_plans:
            raise ValueError(f"Convênio {insurance_id} não é aceito")

        validation = InsuranceValidation(
            insurance_id=insurance_id,
            patient_id=patient_id,
            documents_received=False
        )

        # Armazena o registro
        self._validations[f"{patient_id}:{insurance_id}"] = validation
        return validation

    def mark_documents_received(
        self,
        patient_id: str,
        insurance_id: str
    ) -> InsuranceValidation:
        """
        Marca que os documentos (identidade e carteirinha) foram recebidos.
        """
        key = f"{patient_id}:{insurance_id}"
        if key not in self._validations:
            raise ValueError("Convênio não registrado para este paciente")

        validation = self._validations[key]
        validation.documents_received = True
        return validation

    def can_schedule_appointment(
        self,
        patient_id: str,
        insurance_id: str
    ) -> bool:
        """
        Verifica se o paciente pode agendar consulta com o convênio.
        Retorna True se:
        1. O convênio está entre os aceitos
        2. Os documentos foram recebidos
        """
        key = f"{patient_id}:{insurance_id}"
        validation = self._validations.get(key)
        
        if not validation:
            return False
            
        return validation.is_valid_for_scheduling()

    def get_insurance(
        self,
        patient_id: str,
        insurance_id: str
    ) -> Optional[InsuranceValidation]:
        """Retorna o registro do convênio para um paciente."""
        key = f"{patient_id}:{insurance_id}"
        return self._validations.get(key)

    def format_validation_message(self, validation: InsuranceValidation) -> str:
        """Formata mensagem amigável sobre o status do convênio."""
        plan = self._accepted_plans[validation.insurance_id]
        message = f"Convênio: {plan.name}\n"
        message += f"Status: {validation.get_validation_message()}\n"
        
        if validation.is_valid():
            message += "✅ Seu convênio está válido para agendamento"
        else:
            message += "❌ Não é possível agendar com este convênio no momento"
        
        return message 