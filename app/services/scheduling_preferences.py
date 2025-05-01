from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, time, timedelta
from app.config.clinic_settings import ClinicSettings

@dataclass
class PatientPreferences:
    """Preferências de agendamento do paciente"""
    preferred_days: List[str]  # ['monday', 'tuesday', etc]
    preferred_time_ranges: List[tuple[time, time]]  # [(time(8,30), time(12,15)), etc]
    preferred_duration: int  # em minutos
    avoid_lunch_time: bool = True
    avoid_rush_hour: bool = True

class SchedulingOptimizer:
    """
    Otimizador de horários de agendamento.
    Considera apenas as preferências do paciente para sugerir os melhores horários.
    O ChatGPT será responsável por considerar o histórico e padrões de agendamento.
    """
    
    def __init__(self):
        self.working_hours = ClinicSettings.WORKING_HOURS
    
    def get_optimal_slots(self, 
                         available_slots: List[datetime],
                         preferences: PatientPreferences,
                         duration: int = ClinicSettings.DEFAULT_APPOINTMENT_DURATION) -> List[datetime]:
        """
        Retorna uma lista de horários otimizados baseados nas preferências do paciente.
        
        Args:
            available_slots: Lista de horários disponíveis
            preferences: Preferências do paciente
            duration: Duração da consulta em minutos
            
        Returns:
            List[datetime]: Lista de horários otimizados, ordenados por prioridade
        """
        if not available_slots:
            return []
            
        scored_slots = []
        
        for slot in available_slots:
            score = self._calculate_slot_score(slot, preferences, duration)
            scored_slots.append((slot, score))
        
        # Ordena os slots por pontuação (maior primeiro)
        scored_slots.sort(key=lambda x: x[1], reverse=True)
        
        # Retorna apenas os slots, sem as pontuações
        return [slot for slot, _ in scored_slots]
    
    def _calculate_slot_score(self, 
                            slot: datetime,
                            preferences: PatientPreferences,
                            duration: int) -> float:
        """
        Calcula a pontuação de um horário específico baseado nas preferências do paciente.
        
        Returns:
            float: Score between 0.0 and 5.0, where:
            - 2.0 points for matching preferred days and time ranges
            - 1.5 points for being earlier in the day (normalized)
            - 1.5 points for being within working hours
        """
        score = 0.0
        
        # Base score for matching preferences (2.0 points)
        if self._matches_preferences(slot, preferences):
            score += 2.0
        
        # Score for time of day (1.5 points)
        # Earlier slots get higher scores (normalized to time range)
        day_start = datetime.combine(slot.date(), time(8, 0))  # 8:00 AM reference
        day_end = datetime.combine(slot.date(), time(18, 0))   # 6:00 PM reference
        time_score = 1.5 * (1 - (slot - day_start).total_seconds() / (day_end - day_start).total_seconds())
        score += time_score
        
        # Score for being within working hours (1.5 points)
        if self._is_within_working_hours(slot, duration):
            score += 1.5
        
        return score
    
    def _matches_preferences(self, 
                           slot: datetime,
                           preferences: PatientPreferences) -> bool:
        """Verifica se o horário atende às preferências do paciente"""
        # Verifica dia da semana
        if slot.strftime('%A').lower() not in preferences.preferred_days:
            return False
        
        # Verifica faixa de horário
        slot_time = slot.time()
        for start_time, end_time in preferences.preferred_time_ranges:
            if start_time <= slot_time <= end_time:
                return True
        
        return False
    
    def _is_within_working_hours(self, slot: datetime, duration: int) -> bool:
        """Verifica se o horário está dentro do horário de funcionamento"""
        day = slot.strftime('%A').lower()
        if day not in self.working_hours:
            return False
            
        hours = self.working_hours[day]
        slot_time = slot.time()
        slot_end = (slot + timedelta(minutes=duration)).time()
        
        return (hours['start'] <= slot_time and 
                slot_end <= hours['end']) 