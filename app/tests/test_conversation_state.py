from datetime import datetime
import pytest
from app.services.conversation_state import ConversationState, ConversationManager

def test_conversation_state_initialization():
    """Testa a inicialização do gerenciador de estados"""
    manager = ConversationManager()
    phone = "5511999999999"
    
    # Verifica estado inicial
    assert manager.get_state(phone) == ConversationState.INITIAL
    assert manager.get_data(phone) == {}

def test_state_transitions():
    """Testa as transições de estado"""
    manager = ConversationManager()
    phone = "5511999999999"
    
    # Transição para WAITING_FOR_DATE
    manager.set_state(phone, ConversationState.WAITING_FOR_DATE)
    assert manager.get_state(phone) == ConversationState.WAITING_FOR_DATE
    
    # Transição para WAITING_FOR_TIME
    manager.set_state(phone, ConversationState.WAITING_FOR_TIME)
    assert manager.get_state(phone) == ConversationState.WAITING_FOR_TIME
    
    # Transição para WAITING_FOR_CONFIRMATION
    manager.set_state(phone, ConversationState.WAITING_FOR_CONFIRMATION)
    assert manager.get_state(phone) == ConversationState.WAITING_FOR_CONFIRMATION
    
    # Transição para COMPLETED
    manager.set_state(phone, ConversationState.COMPLETED)
    assert manager.get_state(phone) == ConversationState.COMPLETED

def test_data_management():
    """Testa o gerenciamento de dados da conversação"""
    manager = ConversationManager()
    phone = "5511999999999"
    
    # Adiciona dados
    manager.update_data(phone, {"date": "2024-05-01"})
    assert manager.get_data(phone) == {"date": "2024-05-01"}
    
    # Atualiza dados
    manager.update_data(phone, {"time": "14:30"})
    assert manager.get_data(phone) == {"date": "2024-05-01", "time": "14:30"}
    
    # Reseta conversação
    manager.reset_conversation(phone)
    assert manager.get_data(phone) == {}
    assert manager.get_state(phone) == ConversationState.INITIAL

def test_date_validation():
    """Testa a validação de datas"""
    manager = ConversationManager()
    
    # Datas válidas
    assert manager.is_valid_date("2024-05-01") == True
    assert manager.is_valid_date("2024-12-31") == True
    
    # Datas inválidas
    assert manager.is_valid_date("2024-13-01") == False
    assert manager.is_valid_date("2024-05-32") == False
    assert manager.is_valid_date("01-05-2024") == False
    assert manager.is_valid_date("invalid") == False

def test_time_validation():
    """Testa a validação de horários"""
    manager = ConversationManager()
    
    # Horários válidos
    assert manager.is_valid_time("09:00") == True
    assert manager.is_valid_time("14:30") == True
    assert manager.is_valid_time("23:59") == True
    
    # Horários inválidos
    assert manager.is_valid_time("24:00") == False
    assert manager.is_valid_time("14:60") == False
    assert manager.is_valid_time("invalid") == False
    assert manager.is_valid_time("14:30:00") == False 