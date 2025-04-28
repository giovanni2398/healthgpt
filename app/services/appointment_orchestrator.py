from datetime import datetime
from typing import Optional, List

from app.services.calendar_service import create_calendar_event
from app.services.whatsapp_service import WhatsAppService
from app.services.scheduling_service import SchedulingService
from app.services.notification_service import NotificationService
from app.services.notification_log_service import NotificationLogService

class AppointmentOrchestrator:
    """
    Serviço que orquestra o processo de agendamento,
    integrando os serviços de calendário, WhatsApp e agendamento.
    """
    
    # Lista de convênios aceitos
    ACCEPTED_INSURANCES = ["Unimed", "Amil", "Bradesco Saúde", "SulAmérica"]
    
    def __init__(self):
        self.scheduling_service = SchedulingService()
        self.whatsapp_service = WhatsAppService()
        self.notification_service = NotificationService(self.whatsapp_service)
        self.notification_log_service = NotificationLogService()
    
    def validate_insurance(self, insurance: str) -> bool:
        """Valida se o convênio é aceito."""
        return insurance in self.ACCEPTED_INSURANCES
    
    def schedule_appointment(
        self,
        patient_id: str,
        patient_name: str,
        patient_phone: str,
        slot_id: str,
        reason: str,
        is_private: bool = True,
        insurance: Optional[str] = None,
        insurance_card_url: Optional[str] = None,
        id_document_url: Optional[str] = None,
        sent_by: str = "system"
    ) -> bool:
        """
        Realiza o processo completo de agendamento:
        1. Valida o convênio (se não for particular)
        2. Cria o agendamento no sistema
        3. Cria o evento no Google Calendar
        4. Envia confirmação via WhatsApp
        5. Formata a mensagem de lembrete para envio manual
        6. Cria um log da notificação
        
        Args:
            patient_id: ID do paciente
            patient_name: Nome do paciente
            patient_phone: Telefone do paciente
            slot_id: ID do slot selecionado
            reason: Motivo da consulta
            is_private: Se é consulta particular (True) ou por convênio (False)
            insurance: Nome do convênio (se não for particular)
            insurance_card_url: URL da carteirinha do convênio
            id_document_url: URL do documento de identificação
            sent_by: Nome do usuário que está realizando o agendamento
            
        Returns:
            bool: True se o agendamento foi realizado com sucesso
        """
        try:
            # 1. Valida o convênio (se não for particular)
            if not is_private:
                if not insurance:
                    self.whatsapp_service.send_message(
                        patient_phone,
                        "Por favor, informe o nome do convênio para prosseguir com o agendamento."
                    )
                    return False
                
                if not self.validate_insurance(insurance):
                    self.whatsapp_service.send_message(
                        patient_phone,
                        "Desculpe, mas não atendemos este convênio. Por favor, verifique os convênios aceitos."
                    )
                    return False
                
                if not insurance_card_url:
                    self.whatsapp_service.send_message(
                        patient_phone,
                        "Por favor, envie uma foto da sua carteirinha do convênio para prosseguir."
                    )
                    return False
            
            # Valida documento de identificação
            if not id_document_url:
                self.whatsapp_service.send_message(
                    patient_phone,
                    "Por favor, envie uma foto do seu documento de identificação para prosseguir."
                )
                return False
            
            # 2. Cria o agendamento no sistema
            appointment = self.scheduling_service.create_appointment(
                patient_id=patient_id,
                patient_name=patient_name,
                slot_id=slot_id,
                reason=reason,
                is_private=is_private,
                insurance=insurance,
                insurance_card_url=insurance_card_url,
                id_document_url=id_document_url
            )
            
            if not appointment:
                print("Falha ao criar agendamento no sistema")
                return False
            
            # 3. Cria o evento no Google Calendar
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
            
            # 4. Envia confirmação via WhatsApp
            confirmation_sent = self.whatsapp_service.send_appointment_confirmation(
                phone=patient_phone,
                patient_name=patient_name,
                appointment_date=appointment.start_time,
                reason=reason
            )
            
            if not confirmation_sent:
                print("Falha ao enviar confirmação via WhatsApp")
                return False
            
            # 5. Formata a mensagem de lembrete para envio manual
            reminder_message = self.notification_service.format_appointment_reminder(
                patient_name=patient_name,
                appointment_date=appointment.start_time
            )
            
            # 6. Cria um log da notificação
            log = self.notification_log_service.create_log(
                patient_name=patient_name,
                appointment_date=appointment.start_time,
                message=reminder_message,
                sent_by=sent_by,
                notes=f"Agendamento {'particular' if is_private else 'por convênio'} criado para {reason}"
            )
            
            print(f"Agendamento realizado com sucesso para {patient_name}")
            print("\nMensagem de lembrete formatada para envio manual:")
            print(reminder_message)
            print(f"\nLog de notificação criado com ID: {log.id}")
            
            return True
            
        except Exception as e:
            print(f"Erro durante o processo de agendamento: {e}")
            return False 