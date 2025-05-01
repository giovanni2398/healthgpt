from enum import Enum
from typing import Dict, Optional
from datetime import datetime

class ConversationState(Enum):
    """
    Estados possíveis de uma conversação com o bot.
    """
    INITIAL = "initial"
    WAITING_FOR_DATE = "waiting_for_date"
    WAITING_FOR_TIME = "waiting_for_time"
    WAITING_FOR_CONFIRMATION = "waiting_for_confirmation"
    WAITING_FOR_INSURANCE_DOCS = "waiting_for_insurance_docs"
    COMPLETED = "completed"
    ERROR = "error"

class ConversationManager:
    """
    Gerenciador de estados e dados das conversações.
    """
    def __init__(self):
        self.conversations: Dict[str, Dict] = {}

    def get_state(self, phone: str) -> ConversationState:
        """
        Obtém o estado atual de uma conversação.
        
        Args:
            phone: Número de telefone do usuário
            
        Returns:
            ConversationState: Estado atual da conversação
        """
        if phone not in self.conversations:
            self.conversations[phone] = {
                "state": ConversationState.INITIAL,
                "data": {}
            }
        return self.conversations[phone]["state"]

    def set_state(self, phone: str, state: ConversationState) -> None:
        """
        Define o estado de uma conversação.
        
        Args:
            phone: Número de telefone do usuário
            state: Novo estado da conversação
        """
        if phone not in self.conversations:
            self.conversations[phone] = {
                "state": state,
                "data": {}
            }
        else:
            self.conversations[phone]["state"] = state

    def get_data(self, phone: str) -> Dict:
        """
        Obtém os dados de uma conversação.
        
        Args:
            phone: Número de telefone do usuário
            
        Returns:
            Dict: Dados da conversação
        """
        if phone not in self.conversations:
            self.conversations[phone] = {
                "state": ConversationState.INITIAL,
                "data": {}
            }
        return self.conversations[phone]["data"]

    def update_data(self, phone: str, data: Dict) -> None:
        """
        Atualiza os dados de uma conversação.
        
        Args:
            phone: Número de telefone do usuário
            data: Novos dados a serem adicionados/atualizados
        """
        if phone not in self.conversations:
            self.conversations[phone] = {
                "state": ConversationState.INITIAL,
                "data": data
            }
        else:
            self.conversations[phone]["data"].update(data)

    def reset_conversation(self, phone: str) -> None:
        """Reseta a conversação para o estado inicial"""
        self.conversations[phone] = {
            "state": ConversationState.INITIAL,
            "data": {}
        }

    def is_valid_date(self, date_str: str) -> bool:
        """
        Verifica se uma string representa uma data válida no formato YYYY-MM-DD.
        
        Args:
            date_str: String com a data a ser validada
            
        Returns:
            bool: True se a data for válida, False caso contrário
        """
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def is_valid_time(self, time_str: str) -> bool:
        """
        Verifica se uma string representa um horário válido no formato HH:MM.
        
        Args:
            time_str: String com o horário a ser validado
            
        Returns:
            bool: True se o horário for válido, False caso contrário
        """
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False 