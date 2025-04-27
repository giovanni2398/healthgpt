from typing import Dict
from app.models.insurance import InsurancePlan

# Configuração dos planos de convênio aceitos
ACCEPTED_INSURANCE_PLANS: Dict[str, InsurancePlan] = {
    "unimed": InsurancePlan(
        id="unimed",
        name="Unimed"
    ),
    "amil": InsurancePlan(
        id="amil",
        name="Amil"
    ),
    "bradesco": InsurancePlan(
        id="bradesco",
        name="Bradesco Saúde"
    ),
    "sulamerica": InsurancePlan(
        id="sulamerica",
        name="SulAmérica"
    )
} 