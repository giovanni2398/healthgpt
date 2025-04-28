from datetime import datetime
from typing import Optional
from app.services.whatsapp_service import WhatsAppService

class NotificationService:
    def __init__(self, whatsapp_service: WhatsAppService):
        """
        Inicializa o serviço de notificações com um cliente WhatsApp.
        """
        self.whatsapp_service = whatsapp_service

    def format_appointment_reminder(self, patient_name: str, appointment_date: datetime) -> str:
        """
        Formata a mensagem de lembrete de consulta para ser enviada manualmente via WhatsApp Business.
        
        Args:
            patient_name (str): Nome do paciente
            appointment_date (datetime): Data e hora da consulta
            
        Returns:
            str: Mensagem formatada pronta para ser enviada
        """
        # Inclui data e hora combinadas e informação de reagendamento
        return (
            f"Olá {patient_name},\n\n"
            f"Este é um lembrete da sua consulta agendada para: {appointment_date.strftime('%d/%m/%Y às %H:%M')}\n\n"
            "Por favor, chegue com 15 minutos de antecedência.\n"
            "Se precisar remarcar, entre em contato conosco.\n\n"
            "Atenciosamente,\n"
            "Equipe HealthGPT"
        )

    def send_appointment_reminder(self, patient_data: dict, appointment_date: datetime) -> None:
        """
        Envia o lembrete de consulta via WhatsApp.
        """
        message = self.format_appointment_reminder(
            patient_data.get("name"),
            appointment_date
        )
        # Usa o serviço WhatsApp para enviar a mensagem
        self.whatsapp_service.send_message(
            patient_data.get("phone"),
            message
        )
        
    def schedule_reminder(
        self,
        patient_id: str,
        patient_name: str,
        patient_phone: str,
        appointment_date: datetime,
        reminder_date: datetime
    ) -> bool:
        """
        Agenda um lembrete de consulta para ser enviado em uma data específica.
        
        Args:
            patient_id (str): ID do paciente
            patient_name (str): Nome do paciente
            patient_phone (str): Telefone do paciente
            appointment_date (datetime): Data e hora da consulta
            reminder_date (datetime): Data e hora para enviar o lembrete
            
        Returns:
            bool: True se o lembrete foi agendado com sucesso
        """
        try:
            # Formata a mensagem de lembrete
            message = self.format_appointment_reminder(patient_name, appointment_date)
            
            # Agenda o envio da mensagem
            # TODO: Implementar o agendamento real da mensagem
            # Por enquanto, apenas retorna True para simular sucesso
            return True
            
        except Exception as e:
            print(f"Erro ao agendar lembrete: {str(e)}")
            return False 