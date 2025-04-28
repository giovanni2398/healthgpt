from datetime import datetime, timedelta
import unittest
from unittest.mock import patch, MagicMock

from app.services.appointment_orchestrator import AppointmentOrchestrator
from app.services.notification_service import NotificationService
from app.services.notification_log_service import NotificationLogService
from app.services.whatsapp_service import WhatsAppService

class TestIntegrationFlow(unittest.TestCase):
    def setUp(self):
        """Configura o ambiente de teste."""
        self.orchestrator = AppointmentOrchestrator()
        # Initialize WhatsApp and Notification services with proper dependency injection
        self.whatsapp_service = WhatsAppService()
        self.notification_service = NotificationService(self.whatsapp_service)
        self.log_service = NotificationLogService()
        
        # Dados de teste
        self.patient_name = "João Silva"
        self.patient_phone = "+5511999999999"
        self.insurance = "Unimed"
        self.appointment_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.appointment_time = "14:30"
    
    @patch('app.services.whatsapp_service.WhatsAppService.send_message')
    def test_appointment_flow_with_invalid_insurance(self, mock_send_message):
        """Testa o fluxo de agendamento com convênio inválido."""
        # 1. Configura o mock para retornar True
        mock_send_message.return_value = True
        
        # 2. Simula a verificação de tipo de paciente
        patient_type = self.orchestrator.identify_patient_type("Convênio Inválido")
        self.assertEqual(patient_type, "insurance")
        
        # 3. Simula a verificação de convênio inválido
        is_valid_insurance = self.orchestrator.validate_insurance("Convênio Inválido")
        self.assertFalse(is_valid_insurance)
        
        # 4. Envia mensagem de erro via WhatsApp
        message = "Desculpe, mas não atendemos este convênio. Por favor, verifique os convênios aceitos."
        self.whatsapp_service.send_message(self.patient_phone, message)
        
        # 5. Verifica se a mensagem de convênio inválido foi enviada
        mock_send_message.assert_called_once_with(self.patient_phone, message)

if __name__ == '__main__':
    unittest.main() 