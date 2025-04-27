from datetime import datetime, timedelta
import unittest
from unittest.mock import patch, MagicMock

from app.services.appointment_orchestrator import AppointmentOrchestrator

# Mock do módulo calendar_service
calendar_service_mock = MagicMock()

class TestAppointmentOrchestrator(unittest.TestCase):
    def setUp(self):
        """Configura o ambiente de teste."""
        self.orchestrator = AppointmentOrchestrator()
        self.patient_id = "123"
        self.patient_name = "João Silva"
        self.patient_phone = "+5511999999999"
        self.reason = "Consulta de rotina"
        
        # Cria um slot para teste
        now = datetime.now()
        self.slot = self.orchestrator.scheduling_service.slot_service.create_slot(
            start_time=now + timedelta(days=1, hours=10),
            end_time=now + timedelta(days=1, hours=10, minutes=30)
        )
    
    def test_schedule_appointment_success(self):
        """Testa o processo completo de agendamento com sucesso."""
        # Configura os mocks
        with patch('app.services.appointment_orchestrator.create_calendar_event') as mock_create_event, \
             patch.object(self.orchestrator.whatsapp_service, 'send_appointment_confirmation') as mock_send_confirmation:
            
            # Configura o comportamento dos mocks
            mock_create_event.return_value = {"id": "event123"}
            mock_send_confirmation.return_value = True
            
            # Tenta agendar
            success = self.orchestrator.schedule_appointment(
                patient_id=self.patient_id,
                patient_name=self.patient_name,
                patient_phone=self.patient_phone,
                slot_id=self.slot.id,
                reason=self.reason
            )
            
            # Verifica se o processo foi bem sucedido
            self.assertTrue(success)
            
            # Verifica se os mocks foram chamados
            mock_create_event.assert_called_once()
            mock_send_confirmation.assert_called_once()
    
    def test_schedule_appointment_failure(self):
        """Testa o processo de agendamento com falha."""
        # Configura os mocks
        with patch('app.services.appointment_orchestrator.create_calendar_event') as mock_create_event, \
             patch.object(self.orchestrator.whatsapp_service, 'send_appointment_confirmation') as mock_send_confirmation:
            
            # Configura o mock para lançar uma exceção
            mock_create_event.side_effect = Exception("Erro ao criar evento")
            
            # Tenta agendar
            success = self.orchestrator.schedule_appointment(
                patient_id=self.patient_id,
                patient_name=self.patient_name,
                patient_phone=self.patient_phone,
                slot_id=self.slot.id,
                reason=self.reason
            )
            
            # Verifica se o processo falhou
            self.assertFalse(success)
            
            # Verifica se o WhatsApp não foi chamado
            mock_send_confirmation.assert_not_called()

if __name__ == '__main__':
    unittest.main() 