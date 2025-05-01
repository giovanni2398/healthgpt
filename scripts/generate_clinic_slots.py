#!/usr/bin/env python
"""
Script para gerar slots de acordo com os horários reais da clínica:
- Terça, quinta e sábado: 8h30 às 12h15 (slots de 45 minutos)
- Segunda, quarta e sexta: 14h00 às 17h45 (slots de 45 minutos)
"""

import os
import sys
from datetime import datetime, timedelta, time
from pathlib import Path

# Adiciona o diretório raiz ao path para poder importar os módulos da aplicação
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.slot_management_service import SlotManagementService

def main():
    """Gera slots para as próximas semanas com base nos horários da clínica."""
    # Garantir que o diretório de dados existe
    os.makedirs("data", exist_ok=True)
    
    # Inicializar o serviço de gerenciamento de slots
    service = SlotManagementService(db_path="data/slots.db")
    
    # Obter data atual e ajustar para o início do dia
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Período para gerar slots (padrão: 8 semanas)
    weeks_ahead = 8
    
    # Duração padrão dos slots (45 minutos)
    slot_duration = timedelta(minutes=45)
    
    # Limpar slots antigos
    removed = service.clear_old_slots()
    print(f"Slots antigos removidos: {removed}")
    
    # Gerar slots para dias específicos (terça, quinta, sábado) - manhã
    morning_slots = generate_slots_for_days(
        service=service,
        start_date=today,
        weeks_ahead=weeks_ahead,
        slot_duration=slot_duration,
        days_of_week=[1, 3, 5],  # 0=Segunda, 1=Terça, ..., 5=Sábado, 6=Domingo
        start_time=time(8, 30),  # 8:30
        end_time=time(12, 15)    # 12:15
    )
    
    # Gerar slots para dias específicos (segunda, quarta, sexta) - tarde
    afternoon_slots = generate_slots_for_days(
        service=service,
        start_date=today,
        weeks_ahead=weeks_ahead,
        slot_duration=slot_duration,
        days_of_week=[0, 2, 4],  # 0=Segunda, 1=Terça, ..., 6=Domingo
        start_time=time(14, 0),  # 14:00
        end_time=time(17, 45)    # 17:45
    )
    
    total_slots = morning_slots + afternoon_slots
    print(f"Total de slots gerados: {total_slots}")
    print(f"Slots gerados para as próximas {weeks_ahead} semanas")


def generate_slots_for_days(service, start_date, weeks_ahead, slot_duration, 
                           days_of_week, start_time, end_time):
    """
    Gera slots para dias específicos da semana e horários específicos.
    
    Args:
        service: SlotManagementService
        start_date: Data inicial
        weeks_ahead: Número de semanas à frente
        slot_duration: Duração de cada slot
        days_of_week: Lista de dias da semana (0=Segunda, 6=Domingo)
        start_time: Horário de início (objeto time)
        end_time: Horário de fim (objeto time)
        
    Returns:
        Número de slots gerados
    """
    end_date = start_date + timedelta(weeks=weeks_ahead)
    current_date = start_date
    
    # Lista para armazenar todos os slots gerados
    all_slots = []
    
    # Para cada dia no período
    while current_date <= end_date:
        # Verificar se o dia da semana está na lista de dias desejados
        if current_date.weekday() in days_of_week:
            # Criar datetime para o horário de início e fim
            day_start = datetime.combine(current_date.date(), start_time)
            day_end = datetime.combine(current_date.date(), end_time)
            
            # Criar slots para este dia
            slot_start = day_start
            while slot_start + slot_duration <= day_end:
                slot_end = slot_start + slot_duration
                
                # Criar o slot
                slot_id = service.slot_service.create_slot(slot_start, slot_end)
                all_slots.append(slot_id)
                
                # Avançar para o próximo horário
                slot_start = slot_end
        
        # Avançar para o próximo dia
        current_date += timedelta(days=1)
    
    # Salvar todos os slots gerados no banco de dados
    service._init_db()  # Garantir que o banco está inicializado
    conn = service._get_connection()
    cursor = conn.cursor()
    
    for slot_id in all_slots:
        slot = service.slot_service.get_slot(slot_id)
        cursor.execute(
            '''
            INSERT OR REPLACE INTO slots 
            (id, start_time, end_time, is_available, appointment_id)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (
                slot["id"],
                slot["start_time"].isoformat(),
                slot["end_time"].isoformat(),
                1 if slot["is_available"] else 0,
                slot["appointment_id"]
            )
        )
    
    conn.commit()
    conn.close()
    
    return len(all_slots)


if __name__ == "__main__":
    main() 