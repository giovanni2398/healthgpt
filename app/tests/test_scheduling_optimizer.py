from datetime import datetime, time
import pytest
from app.services.scheduling_preferences import (
    SchedulingOptimizer,
    PatientPreferences
)
from app.config.clinic_settings import ClinicSettings

@pytest.fixture
def optimizer():
    """Fixture para criar uma instância do otimizador"""
    return SchedulingOptimizer()

@pytest.fixture
def sample_preferences():
    return PatientPreferences(
        preferred_days=['monday', 'wednesday', 'friday'],
        preferred_time_ranges=[(time(9, 0), time(12, 0)), (time(14, 0), time(17, 0))],
        preferred_duration=60,
        avoid_lunch_time=True,
        avoid_rush_hour=True
    )

@pytest.fixture
def sample_slots():
    return [
        datetime(2024, 3, 18, 9, 0),   # Monday, 9:00 AM
        datetime(2024, 3, 18, 12, 0),  # Monday, 12:00 PM (lunch time)
        datetime(2024, 3, 18, 17, 0),  # Monday, 5:00 PM (rush hour)
        datetime(2024, 3, 19, 10, 0),  # Tuesday, 10:00 AM
        datetime(2024, 3, 20, 15, 0),  # Wednesday, 3:00 PM
    ]

@pytest.fixture
def afternoon_preferences():
    """Fixture para criar preferências de horários da tarde"""
    return PatientPreferences(
        preferred_days=['monday', 'wednesday', 'friday'],
        preferred_time_ranges=[(time(14, 0), time(17, 45))],
        preferred_duration=45
    )

@pytest.fixture
def morning_preferences():
    """Fixture para criar preferências de horários da manhã"""
    return PatientPreferences(
        preferred_days=['tuesday', 'thursday', 'saturday'],
        preferred_time_ranges=[(time(8, 30), time(12, 15))],
        preferred_duration=45
    )

def test_get_optimal_slots_with_preferences(optimizer, sample_preferences, sample_slots):
    optimal_slots = optimizer.get_optimal_slots(sample_slots, sample_preferences)
    
    # Verifica se os slots estão ordenados corretamente
    assert len(optimal_slots) == len(sample_slots)
    
    # Verifica se os slots preferenciais estão na ordem correta
    # Os slots na segunda-feira e quarta-feira devem ter prioridade
    monday_slots = [slot for slot in optimal_slots if slot.strftime('%A').lower() == 'monday']
    wednesday_slots = [slot for slot in optimal_slots if slot.strftime('%A').lower() == 'wednesday']
    
    # Deve haver pelo menos um slot de segunda e um de quarta
    assert any(monday_slots)
    assert any(wednesday_slots)
    
    # Verifica se os slots não preferenciais são os últimos
    tuesday_slots = [slot for slot in optimal_slots if slot.strftime('%A').lower() == 'tuesday']
    assert all(optimal_slots.index(tuesday) > optimal_slots.index(monday) 
               for tuesday in tuesday_slots for monday in monday_slots)

def test_get_optimal_slots_empty_input(optimizer, sample_preferences):
    optimal_slots = optimizer.get_optimal_slots([], sample_preferences)
    assert optimal_slots == []

def test_calculate_slot_score(optimizer, sample_preferences):
    # Testa um slot que atende todas as preferências
    good_slot = datetime(2024, 3, 18, 10, 0)  # Monday, 10:00 AM
    good_score = optimizer._calculate_slot_score(good_slot, sample_preferences, 60)
    assert good_score > 0
    
    # Testa um slot durante o horário de almoço
    lunch_slot = datetime(2024, 3, 18, 12, 30)  # Monday, 12:30 PM
    lunch_score = optimizer._calculate_slot_score(lunch_slot, sample_preferences, 60)
    assert lunch_score < good_score
    
    # Testa um slot durante o horário de pico
    rush_slot = datetime(2024, 3, 18, 18, 0)  # Monday, 6:00 PM
    rush_score = optimizer._calculate_slot_score(rush_slot, sample_preferences, 60)
    assert rush_score < good_score

def test_matches_preferences(optimizer, sample_preferences):
    # Testa um slot que atende às preferências
    good_slot = datetime(2024, 3, 18, 10, 0)  # Monday, 10:00 AM
    assert optimizer._matches_preferences(good_slot, sample_preferences)
    
    # Testa um slot em um dia não preferido
    bad_day_slot = datetime(2024, 3, 19, 10, 0)  # Tuesday, 10:00 AM
    assert not optimizer._matches_preferences(bad_day_slot, sample_preferences)
    
    # Testa um slot fora do horário preferido
    bad_time_slot = datetime(2024, 3, 18, 8, 0)  # Monday, 8:00 AM
    assert not optimizer._matches_preferences(bad_time_slot, sample_preferences)

def test_get_optimal_slots_afternoon(optimizer, afternoon_preferences):
    """Testa a otimização de slots para horários da tarde"""
    # Cria slots disponíveis para uma segunda-feira
    slots = [
        datetime(2024, 3, 1, 14, 0),   # Segunda, 14h
        datetime(2024, 3, 1, 14, 45),  # Segunda, 14h45
        datetime(2024, 3, 1, 15, 30),  # Segunda, 15h30
        datetime(2024, 3, 1, 16, 15),  # Segunda, 16h15
        datetime(2024, 3, 1, 17, 0)    # Segunda, 17h
    ]
    
    optimal_slots = optimizer.get_optimal_slots(slots, afternoon_preferences)
    
    # Verifica se todos os slots foram mantidos (são todos preferenciais)
    assert len(optimal_slots) == 5
    assert all(slot in slots for slot in optimal_slots)

def test_get_optimal_slots_morning(optimizer, morning_preferences):
    """Testa a otimização de slots para horários da manhã"""
    # Cria slots disponíveis para uma terça-feira
    slots = [
        datetime(2024, 3, 2, 8, 30),   # Terça, 8h30
        datetime(2024, 3, 2, 9, 15),   # Terça, 9h15
        datetime(2024, 3, 2, 10, 0),   # Terça, 10h
        datetime(2024, 3, 2, 10, 45),  # Terça, 10h45
        datetime(2024, 3, 2, 11, 30)   # Terça, 11h30
    ]
    
    optimal_slots = optimizer.get_optimal_slots(slots, morning_preferences)
    
    # Verifica se todos os slots foram mantidos (são todos preferenciais)
    assert len(optimal_slots) == 5
    assert all(slot in slots for slot in optimal_slots)

def test_get_optimal_slots_wrong_day(optimizer, afternoon_preferences):
    """Testa a otimização de slots para um dia não preferencial"""
    # Cria slots disponíveis para uma terça-feira (não preferencial)
    slots = [
        datetime(2024, 3, 2, 14, 0),   # Terça, 14h
        datetime(2024, 3, 2, 14, 45),  # Terça, 14h45
        datetime(2024, 3, 2, 15, 30),  # Terça, 15h30
    ]
    
    optimal_slots = optimizer.get_optimal_slots(slots, afternoon_preferences)
    
    # Verifica se os slots foram ordenados com pontuação menor
    assert len(optimal_slots) == 3
    assert all(slot in slots for slot in optimal_slots)

def test_get_optimal_slots_empty(optimizer, afternoon_preferences):
    """Testa a otimização com lista vazia de slots"""
    optimal_slots = optimizer.get_optimal_slots([], afternoon_preferences)
    assert len(optimal_slots) == 0

def test_matches_preferences_correct_day_and_time(optimizer, afternoon_preferences):
    """Testa se um slot corresponde às preferências (dia e horário corretos)"""
    slot = datetime(2024, 3, 1, 14, 0)  # Segunda, 14h
    assert optimizer._matches_preferences(slot, afternoon_preferences) is True

def test_matches_preferences_wrong_day(optimizer, afternoon_preferences):
    """Testa se um slot não corresponde às preferências (dia errado)"""
    slot = datetime(2024, 3, 2, 14, 0)  # Terça, 14h
    assert optimizer._matches_preferences(slot, afternoon_preferences) is False

def test_matches_preferences_wrong_time(optimizer, afternoon_preferences):
    """Testa se um slot não corresponde às preferências (horário errado)"""
    slot = datetime(2024, 3, 1, 8, 30)  # Segunda, 8h30
    assert optimizer._matches_preferences(slot, afternoon_preferences) is False

def test_is_within_working_hours(optimizer, afternoon_preferences):
    """Testa se um slot está dentro do horário de funcionamento"""
    # Slot dentro do horário (segunda, 14h)
    slot = datetime(2024, 3, 1, 14, 0)
    assert optimizer._is_within_working_hours(slot, 45) is True
    
    # Slot fora do horário (segunda, 18h)
    slot_late = datetime(2024, 3, 1, 18, 0)
    assert optimizer._is_within_working_hours(slot_late, 45) is False
    
    # Slot em dia sem atendimento (domingo)
    slot_sunday = datetime(2024, 3, 3, 14, 0)
    assert optimizer._is_within_working_hours(slot_sunday, 45) is False 