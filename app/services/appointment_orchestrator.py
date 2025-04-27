from datetime import datetime
from typing import Optional

from app.services.calendar_service import create_calendar_event
from app.services.whatsapp_service import WhatsAppService
from app.services.scheduling_service import SchedulingService

class AppointmentOrchestrator:
    """
    Serviço que orquestra o processo de agendamento,
    integrando os serviços de calendário, WhatsApp e agendamento.
    """
    
    def __init__(self):
        self.scheduling_service = SchedulingService()
        self.whatsapp_service = WhatsAppService()
    
    def schedule_appointment(
        self,
        patient_id: str,
        patient_name: str,
        patient_phone: str,
        slot_id: str,
        reason: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Realiza o processo completo de agendamento:
        1. Cria o agendamento no sistema
        2. Cria o evento no Google Calendar
        3. Envia confirmação via WhatsApp
        
        Args:
            patient_id: ID do paciente
            patient_name: Nome do paciente
            patient_phone: Telefone do paciente
            slot_id: ID do slot selecionado
            reason: Motivo da consulta
            notes: Observações adicionais (opcional)
            
        Returns:
            bool: True se o agendamento foi realizado com sucesso
        """
        try:
            # 1. Cria o agendamento no sistema
            appointment = self.scheduling_service.create_appointment(
                patient_id=patient_id,
                slot_id=slot_id,
                reason=reason,
                notes=notes
            )
            
            if not appointment:
                print("Falha ao criar agendamento no sistema")
                return False
            
            # 2. Cria o evento no Google Calendar
            calendar_event = create_calendar_event(
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                patient_name=patient_name,
                patient_phone=patient_phone,
                reason=reason
            )
            
            if not calendar_event:
                print("Falha ao criar evento no calendário")
                return False
            
            # 3. Envia confirmação via WhatsApp
            confirmation_sent = self.whatsapp_service.send_appointment_confirmation(
                phone=patient_phone,
                patient_name=patient_name,
                appointment_date=appointment.start_time,
                reason=reason
            )
            
            if not confirmation_sent:
                print("Falha ao enviar confirmação via WhatsApp")
                return False
            
            print(f"Agendamento realizado com sucesso para {patient_name}")
            return True
            
        except Exception as e:
            print(f"Erro durante o processo de agendamento: {e}")
            return False 