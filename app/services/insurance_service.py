from typing import Dict, List, Optional
from datetime import datetime, timedelta
from ..models.insurance import InsurancePlan, InsuranceValidation

class InsuranceService:
    """Serviço para gerenciamento e validação de convênios."""
    
    def __init__(self):
        # Simula um banco de dados de planos aceitos
        self._accepted_plans: Dict[str, InsurancePlan] = {
            "unimed-basic": InsurancePlan(
                id="unimed-basic",
                name="Unimed Básico",
                provider="Unimed",
                coverage_type="basic",
                waiting_period_days=30,
                active=True
            ),
            "amil-premium": InsurancePlan(
                id="amil-premium",
                name="Amil Premium",
                provider="Amil",
                coverage_type="premium",
                waiting_period_days=0,
                active=True
            )
        }
        
        # Simula um banco de dados de validações de convênio
        self._validations: Dict[str, InsuranceValidation] = {}

    def get_accepted_plans(self) -> List[InsurancePlan]:
        """Retorna lista de planos aceitos ativos."""
        return [plan for plan in self._accepted_plans.values() if plan.active]

    def validate_insurance(
        self,
        patient_id: str,
        insurance_id: str,
        card_number: str
    ) -> InsuranceValidation:
        """
        Valida o convênio de um paciente.
        Em um ambiente real, isso faria uma chamada à API do convênio.
        """
        if insurance_id not in self._accepted_plans:
            raise ValueError(f"Convênio {insurance_id} não é aceito")

        plan = self._accepted_plans[insurance_id]
        
        # Simula validação com o provedor do convênio
        validation = InsuranceValidation(
            insurance_id=insurance_id,
            patient_id=patient_id,
            card_number=card_number,
            valid_until=datetime.now() + timedelta(days=365),  # Simula validade de 1 ano
            status="active"
        )

        # Aplica período de carência se necessário
        if plan.waiting_period_days > 0:
            validation.status = "waiting_period"
            validation.waiting_period_ends = datetime.now() + timedelta(days=plan.waiting_period_days)

        # Armazena a validação
        self._validations[f"{patient_id}:{insurance_id}"] = validation
        return validation

    def get_validation(
        self,
        patient_id: str,
        insurance_id: str
    ) -> Optional[InsuranceValidation]:
        """Retorna a validação existente para um paciente/convênio."""
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