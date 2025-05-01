import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class InsuranceInfo:
    """Estrutura para armazenar informações do convênio"""
    provider: str
    card_number: str
    validity: datetime
    patient_name: str
    patient_id: str

class InsuranceService:
    """
    Serviço para validação e verificação de convênios.
    Implementa a lógica de validação de convênios aceitos e documentos.
    """
    
    # Lista de convênios aceitos
    ACCEPTED_INSURANCES = [
        "unimed",
        "bradesco",
        "sulamerica",
        "amil",
        "porto seguro",
        "notre dame",
        "intermédica",
        "hapvida",
        "santa casa",
        "cassi"
    ]
    
    def __init__(self):
        self.verified_insurances: Dict[str, InsuranceInfo] = {}
    
    def validate_insurance_provider(self, provider: str) -> bool:
        """Valida se o convênio está na lista de aceitos"""
        return provider.lower() in self.ACCEPTED_INSURANCES
    
    def verify_insurance_documents(self, 
                                 provider: str,
                                 card_number: str,
                                 validity: datetime,
                                 patient_name: str,
                                 patient_id: str) -> bool:
        """
        Verifica os documentos do convênio.
        Em um ambiente real, aqui seria feita a validação com a API do convênio.
        """
        if not self.validate_insurance_provider(provider):
            return False
            
        # Simula verificação de documentos
        insurance_info = InsuranceInfo(
            provider=provider,
            card_number=card_number,
            validity=validity,
            patient_name=patient_name,
            patient_id=patient_id
        )
        
        # Armazena as informações verificadas
        self.verified_insurances[card_number] = insurance_info
        return True
    
    def get_insurance_info(self, card_number: str) -> Optional[InsuranceInfo]:
        """Retorna as informações do convênio se estiver verificado"""
        return self.verified_insurances.get(card_number)
    
    def is_insurance_valid(self, card_number: str) -> bool:
        """Verifica se o convênio está ativo e válido"""
        insurance_info = self.get_insurance_info(card_number)
        if not insurance_info:
            return False
            
        return insurance_info.validity > datetime.now() 