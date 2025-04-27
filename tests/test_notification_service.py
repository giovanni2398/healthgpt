from datetime import datetime
import unittest

from services.notification_service import NotificationService

class TestNotificationService(unittest.TestCase):
    def setUp(self):
        """Configura o ambiente de teste."""
        self.notification_service = NotificationService()
        self.patient_name = "João Silva"
        self.appointment_date = datetime(2024, 3, 15, 14, 30)  # 15/03/2024 14:30
    
    def test_format_appointment_reminder(self):
        """Testa a formatação da mensagem de lembrete de consulta."""
        message = self.notification_service.format_appointment_reminder(
            patient_name=self.patient_name,
            appointment_date=self.appointment_date
        )
        
        # Verifica se a mensagem contém as informações necessárias
        self.assertIn(self.patient_name, message)
        self.assertIn("15/03/2024", message)
        self.assertIn("14:30", message)
        self.assertIn("Por favor, chegue com 15 minutos de antecedência", message)
        
        # Verifica se a mensagem está formatada corretamente
        self.assertTrue(message.startswith("\nOlá"))
        self.assertTrue(message.endswith("Equipe HealthGPT\n")) 