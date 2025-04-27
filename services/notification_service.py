from datetime import datetime
from typing import Optional

class NotificationService:
    def __init__(self):
        """
        Inicializa o serviço de notificações.
        Atualmente, as notificações são enviadas manualmente através do WhatsApp Business.
        """
        pass

    def format_appointment_reminder(self, patient_name: str, appointment_date: datetime) -> str:
        """
        Formata a mensagem de lembrete de consulta para ser enviada manualmente via WhatsApp Business.
        
        Args:
            patient_name (str): Nome do paciente
            appointment_date (datetime): Data e hora da consulta
            
        Returns:
            str: Mensagem formatada pronta para ser enviada
        """
        return f"""
Olá {patient_name},

Este é um lembrete da sua consulta agendada para:
*Data:* {appointment_date.strftime('%d/%m/%Y')}
*Horário:* {appointment_date.strftime('%H:%M')}

Por favor, chegue com 15 minutos de antecedência.

Atenciosamente,
Equipe HealthGPT
""" 