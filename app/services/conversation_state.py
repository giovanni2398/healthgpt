from enum import Enum
from typing import Dict, Optional
from datetime import datetime

class ConversationState(Enum):
    """Estados possíveis da conversação"""
    INITIAL = "initial"  # Estado inicial
    WAITING_FOR_DATE = "waiting_for_date"  # Aguardando confirmação de data
    WAITING_FOR_TIME = "waiting_for_time"  # Aguardando confirmação de horário
    WAITING_FOR_CONFIRMATION = "waiting_for_confirmation"  # Aguardando confirmação final
    COMPLETED = "completed"  # Agendamento concluído
    ERROR = "error"  # Estado de erro

class ConversationManager:
    """Gerenciador de estados da conversação"""
    
    def __init__(self):
        self.conversations: Dict[str, Dict] = {}
    
    def get_state(self, phone_number: str) -> ConversationState:
        """Retorna o estado atual da conversação"""
        if phone_number not in self.conversations:
            self.conversations[phone_number] = {
                "state": ConversationState.INITIAL,
                "data": {}
            }
        return self.conversations[phone_number]["state"]
    
    def set_state(self, phone_number: str, state: ConversationState) -> None:
        """Define o estado da conversação"""
        if phone_number not in self.conversations:
            self.conversations[phone_number] = {"data": {}}
        self.conversations[phone_number]["state"] = state
    
    def get_data(self, phone_number: str) -> Dict:
        """Retorna os dados da conversação"""
        if phone_number not in self.conversations:
            self.conversations[phone_number] = {
                "state": ConversationState.INITIAL,
                "data": {}
            }
        return self.conversations[phone_number]["data"]
    
    def update_data(self, phone_number: str, data: Dict) -> None:
        """Atualiza os dados da conversação"""
        if phone_number not in self.conversations:
            self.conversations[phone_number] = {
                "state": ConversationState.INITIAL,
                "data": {}
            }
        self.conversations[phone_number]["data"].update(data)
    
    def reset_conversation(self, phone_number: str) -> None:
        """Reseta a conversação para o estado inicial"""
        self.conversations[phone_number] = {
            "state": ConversationState.INITIAL,
            "data": {}
        }
    
    def is_valid_date(self, date_str: str) -> bool:
        """Valida se a data está em um formato válido"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def is_valid_time(self, time_str: str) -> bool:
        """Valida se o horário está em um formato válido"""
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False 