from datetime import time, datetime, timedelta
from typing import List, Tuple, Dict

class ClinicSettings:
    """Configurações da clínica"""
    
    # Duração padrão das consultas (em minutos)
    DEFAULT_APPOINTMENT_DURATION = 45
    
    # Intervalo entre consultas (em minutos)
    APPOINTMENT_INTERVAL = 45
    
    # Horários de funcionamento por dia
    WORKING_HOURS: Dict[str, Dict[str, time]] = {
        'monday': {'start': time(14, 0), 'end': time(17, 45)},
        'wednesday': {'start': time(14, 0), 'end': time(17, 45)},
        'friday': {'start': time(14, 0), 'end': time(17, 45)},
        'tuesday': {'start': time(8, 30), 'end': time(12, 15)},
        'thursday': {'start': time(8, 30), 'end': time(12, 15)},
        'saturday': {'start': time(8, 30), 'end': time(12, 15)}
    }
    
    # Dias da semana de funcionamento
    WORKING_DAYS = list(WORKING_HOURS.keys())
    
    # Intervalos de horário preferenciais para agendamento
    PREFERRED_TIME_RANGES: List[Tuple[time, time]] = [
        (time(8, 30), time(12, 15)),   # Manhã: 8h30 às 12h15
        (time(14, 0), time(17, 45))    # Tarde: 14h às 17h45
    ]
    
    @classmethod
    def get_available_time_ranges(cls, day: str) -> List[Tuple[time, time]]:
        """
        Retorna os intervalos de horário disponíveis para agendamento
        para um dia específico.
        
        Args:
            day: Dia da semana em inglês (lowercase)
            
        Returns:
            List[Tuple[time, time]]: Lista de intervalos de horário disponíveis
        """
        if day not in cls.WORKING_HOURS:
            return []
            
        hours = cls.WORKING_HOURS[day]
        return [(hours['start'], hours['end'])]
    
    @classmethod
    def get_available_slots(cls, day: str) -> List[time]:
        """
        Retorna todos os slots disponíveis para um dia específico.
        
        Args:
            day: Dia da semana em inglês (lowercase)
            
        Returns:
            List[time]: Lista de horários disponíveis
        """
        if day not in cls.WORKING_HOURS:
            return []
            
        hours = cls.WORKING_HOURS[day]
        slots = []
        current_time = hours['start']
        
        # Gera 5 slots de 45 minutos
        for _ in range(5):
            slots.append(current_time)
            current_time = (datetime.combine(datetime.min, current_time) + 
                          timedelta(minutes=cls.APPOINTMENT_INTERVAL)).time()
            
        return slots 