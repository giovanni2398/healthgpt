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
        self.patient_id = "123"
        self.patient_name = "João Silva"
        self.patient_phone = "+5511999999999"
        self.insurance = "Unimed"
        self.reason = "Consulta de rotina"
        
        # Cria um slot para teste
        now = datetime.now()
        self.slot = self.orchestrator.scheduling_service.slot_service.create_slot(
            start_time=now + timedelta(days=1, hours=10),
            end_time=now + timedelta(days=1, hours=10, minutes=30)
        )
    
    @patch('app.services.appointment_orchestrator.create_calendar_event')
    @patch('app.services.whatsapp_service.WhatsAppService.send_message')
    def test_private_appointment_flow(self, mock_send_message, mock_create_event):
        """Testa o fluxo completo de agendamento particular."""
        # Configura os mocks
        mock_send_message.return_value = True
        mock_create_event.return_value = {"id": "event123"}
        
        # Tenta agendar
        success = self.orchestrator.schedule_appointment(
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            patient_phone=self.patient_phone,
            slot_id=self.slot.id,
            reason=self.reason,
            is_private=True,
            id_document_url="http://example.com/id.pdf"
        )
        
        # Verifica se o agendamento foi bem sucedido
        self.assertTrue(success)
        
        # Verifica se os mocks foram chamados
        mock_create_event.assert_called_once()
        mock_send_message.assert_called()
    
    @patch('app.services.appointment_orchestrator.create_calendar_event')
    @patch('app.services.whatsapp_service.WhatsAppService.send_message')
    def test_insurance_appointment_flow(self, mock_send_message, mock_create_event):
        """Testa o fluxo completo de agendamento por convênio."""
        # Configura os mocks
        mock_send_message.return_value = True
        mock_create_event.return_value = {"id": "event123"}
        
        # Tenta agendar
        success = self.orchestrator.schedule_appointment(
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            patient_phone=self.patient_phone,
            slot_id=self.slot.id,
            reason=self.reason,
            is_private=False,
            insurance=self.insurance,
            insurance_card_url="http://example.com/insurance.pdf",
            id_document_url="http://example.com/id.pdf"
        )
        
        # Verifica se o agendamento foi bem sucedido
        self.assertTrue(success)
        
        # Verifica se os mocks foram chamados
        mock_create_event.assert_called_once()
        mock_send_message.assert_called()
    
    @patch('app.services.whatsapp_service.WhatsAppService.send_message')
    def test_appointment_flow_with_invalid_insurance(self, mock_send_message):
        """Testa o fluxo de agendamento com convênio inválido."""
        # Configura o mock para retornar True
        mock_send_message.return_value = True
        
        # Tenta agendar com convênio inválido
        success = self.orchestrator.schedule_appointment(
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            patient_phone=self.patient_phone,
            slot_id=self.slot.id,
            reason=self.reason,
            is_private=False,
            insurance="Convênio Inválido",
            insurance_card_url="http://example.com/insurance.pdf",
            id_document_url="http://example.com/id.pdf"
        )
        
        # Verifica se o agendamento falhou
        self.assertFalse(success)
        
        # Verifica se a mensagem de erro foi enviada
        mock_send_message.assert_called_with(
            self.patient_phone,
            "Desculpe, mas não atendemos este convênio. Por favor, verifique os convênios aceitos."
        )

if __name__ == '__main__':
    unittest.main() 