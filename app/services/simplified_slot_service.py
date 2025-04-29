from datetime import datetime, timedelta, time
import json
import os
import uuid
from typing import List, Dict, Optional

class SimplifiedSlotService:
    """Serviço simplificado para gerenciar slots de horário com padrões fixos."""
    
    def __init__(self, 
                appointments_file: str = "data/appointments.json",
                schedule_config_file: str = "app/config/clinic_schedule.json"):
        """
        Inicializa o serviço de slots simplificado.
        
        Args:
            appointments_file: Caminho para o arquivo JSON que armazenará os agendamentos
            schedule_config_file: Caminho para o arquivo de configuração de horários
        """
        self.appointments_file = appointments_file
        self.schedule_config_file = schedule_config_file
        self.appointments = self._load_appointments()
        
        # Carregar configurações de horários
        self.config = self._load_schedule_config()
        
        # Configurar a duração dos slots
        self.slot_duration = timedelta(minutes=self.config.get("slot_duration_minutes", 45))
        
        # Inicializar listas para os horários
        self.schedules = []
        
        # Processar cada configuração de horário
        for schedule in self.config.get("schedules", []):
            days = schedule.get("days", [])
            
            # Parsear os horários
            start_time_str = schedule.get("start_time", "09:00")
            end_time_str = schedule.get("end_time", "17:00")
            
            hour_start, minute_start = map(int, start_time_str.split(":"))
            hour_end, minute_end = map(int, end_time_str.split(":"))
            
            self.schedules.append({
                "days": days,
                "start_time": time(hour_start, minute_start),
                "end_time": time(hour_end, minute_end)
            })
    
    def _load_schedule_config(self) -> Dict:
        """Carrega as configurações de horários do arquivo JSON."""
        if not os.path.exists(self.schedule_config_file):
            # Se o arquivo não existir, criar um arquivo padrão
            default_config = {
                "slot_duration_minutes": 45,
                "schedules": [
                    {
                        "days": [1, 3, 5],
                        "description": "Terça, Quinta e Sábado - Manhã",
                        "start_time": "08:30",
                        "end_time": "12:15"
                    },
                    {
                        "days": [0, 2, 4],
                        "description": "Segunda, Quarta e Sexta - Tarde",
                        "start_time": "14:00",
                        "end_time": "17:45"
                    }
                ]
            }
            
            # Garantir que o diretório existe
            os.makedirs(os.path.dirname(os.path.abspath(self.schedule_config_file)), exist_ok=True)
            
            # Salvar configuração padrão
            with open(self.schedule_config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
                
            return default_config
        
        # Se o arquivo existir, carregar as configurações
        try:
            with open(self.schedule_config_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Em caso de erro no arquivo, retornar configuração padrão
            return {
                "slot_duration_minutes": 45,
                "schedules": []
            }
    
    def _load_appointments(self) -> Dict[str, Dict]:
        """Carrega os agendamentos do arquivo JSON."""
        os.makedirs(os.path.dirname(os.path.abspath(self.appointments_file)), exist_ok=True)
        
        if os.path.exists(self.appointments_file):
            try:
                with open(self.appointments_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def _save_appointments(self):
        """Salva os agendamentos no arquivo JSON."""
        with open(self.appointments_file, 'w') as f:
            json.dump(self.appointments, f, indent=2)
    
    def generate_slots(self, start_date: datetime, weeks_ahead: int = 8) -> List[Dict]:
        """
        Gera slots para o período especificado com base nos padrões fixos da clínica.
        
        Args:
            start_date: Data inicial para geração
            weeks_ahead: Número de semanas à frente
            
        Returns:
            Lista de slots gerados
        """
        slots = []
        end_date = start_date + timedelta(weeks=weeks_ahead)
        current_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        while current_date <= end_date:
            weekday = current_date.weekday()
            
            # Verificar cada configuração de horário
            for schedule in self.schedules:
                days = schedule.get("days", [])
                start_time = schedule.get("start_time")
                end_time = schedule.get("end_time")
                
                # Se o dia atual está na lista de dias desta configuração
                if weekday in days:
                    day_start = datetime.combine(current_date.date(), start_time)
                    day_end = datetime.combine(current_date.date(), end_time)
                    
                    slot_start = day_start
                    while slot_start + self.slot_duration <= day_end:
                        slot_end = slot_start + self.slot_duration
                        slot_id = str(uuid.uuid4())
                        
                        # Verificar se o slot já está agendado
                        is_available = self._is_slot_available(slot_start, slot_end)
                        
                        slots.append({
                            "id": slot_id,
                            "start_time": slot_start,
                            "end_time": slot_end,
                            "is_available": is_available
                        })
                        
                        slot_start = slot_end
            
            current_date += timedelta(days=1)
        
        return slots
    
    def _is_slot_available(self, start_time: datetime, end_time: datetime) -> bool:
        """
        Verifica se um slot está disponível (não reservado).
        
        Args:
            start_time: Horário de início do slot
            end_time: Horário de fim do slot
            
        Returns:
            True se o slot estiver disponível, False caso contrário
        """
        # Converter para string ISO para comparação com as chaves no dicionário
        start_iso = start_time.isoformat()
        
        # Verificar se o slot está na lista de agendamentos
        return start_iso not in self.appointments
    
    def get_available_slots(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Obtém os slots disponíveis em um intervalo de datas.
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Lista de slots disponíveis
        """
        all_slots = self.generate_slots(start_date, 
                                       (end_date - start_date).days // 7 + 1)
        
        # Filtrar apenas slots disponíveis e dentro do intervalo
        available_slots = []
        for slot in all_slots:
            if (slot["is_available"] and 
                slot["start_time"] >= start_date and 
                slot["end_time"] <= end_date):
                available_slots.append(slot)
        
        # Ordenar por data/hora
        available_slots.sort(key=lambda s: s["start_time"])
        return available_slots
    
    def book_slot(self, start_time: datetime, appointment_info: Dict) -> bool:
        """
        Reserva um slot para um agendamento.
        
        Args:
            start_time: Horário de início do slot a ser reservado
            appointment_info: Informações do agendamento (nome, motivo, etc.)
            
        Returns:
            True se o agendamento foi realizado com sucesso, False caso contrário
        """
        # Convertemos para string ISO para usar como chave no dicionário
        start_iso = start_time.isoformat()
        
        # Verificar se o slot já está reservado
        if start_iso in self.appointments:
            return False
        
        # Adicionar o agendamento
        self.appointments[start_iso] = appointment_info
        
        # Salvar agendamentos no arquivo
        self._save_appointments()
        
        return True
    
    def cancel_appointment(self, start_time: datetime) -> bool:
        """
        Cancela um agendamento existente.
        
        Args:
            start_time: Horário de início do slot agendado
            
        Returns:
            True se o cancelamento foi realizado com sucesso, False caso contrário
        """
        start_iso = start_time.isoformat()
        
        if start_iso not in self.appointments:
            return False
        
        # Remover o agendamento
        del self.appointments[start_iso]
        
        # Salvar agendamentos no arquivo
        self._save_appointments()
        
        return True
    
    def get_appointment(self, start_time: datetime) -> Optional[Dict]:
        """
        Obtém as informações de um agendamento.
        
        Args:
            start_time: Horário de início do slot agendado
            
        Returns:
            Informações do agendamento ou None se não encontrado
        """
        start_iso = start_time.isoformat()
        return self.appointments.get(start_iso)
    
    def get_all_appointments(self) -> Dict[str, Dict]:
        """
        Obtém todos os agendamentos.
        
        Returns:
            Dicionário com todos os agendamentos
        """
        return self.appointments.copy() 