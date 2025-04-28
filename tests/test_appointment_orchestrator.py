import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from app.services.appointment_orchestrator import AppointmentOrchestrator

# Mock do módulo calendar_service
calendar_service_mock = MagicMock()

class TestAppointmentOrchestrator:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura o ambiente de teste."""
        self.orchestrator = AppointmentOrchestrator()
        self.patient_id = "123"
        self.patient_name = "João Silva"
        self.patient_phone = "+5511999999999"
        self.reason = "Consulta de rotina"
        
        # Cria um slot para teste
        now = datetime.now()
        self.slot_id = self.orchestrator.scheduling_service.slot_service.create_slot(
            start_time=now + timedelta(days=1, hours=10),
            end_time=now + timedelta(days=1, hours=11)
        )
    
    def test_schedule_private_appointment_success(self):
        """Testa o processo completo de agendamento particular com sucesso."""
        # Configura os mocks
        with patch('app.services.appointment_orchestrator.create_calendar_event', new_callable=MagicMock) as mock_create_event, \
             patch.object(self.orchestrator.whatsapp_service, 'send_appointment_confirmation', new_callable=MagicMock) as mock_send_confirmation:
            
            # Configura o comportamento dos mocks
            mock_create_event.return_value = {"id": "event123"}
            mock_send_confirmation.return_value = True
            
            # Tenta agendar
            success = self.orchestrator.schedule_appointment(
                patient_id=self.patient_id,
                patient_name=self.patient_name,
                patient_phone=self.patient_phone,
                slot_id=self.slot_id,
                reason=self.reason,
                is_private=True,
                id_document_url="http://example.com/id.pdf"
            )
            
            # Verifica se o agendamento foi bem sucedido
            assert success is True
            
            # Verifica se os mocks foram chamados
            mock_create_event.assert_called_once()
            mock_send_confirmation.assert_called_once()
            
            # Verifica se a mensagem de lembrete foi formatada corretamente
            # Get the actual slot details to retrieve the datetime object
            slot = self.orchestrator.scheduling_service.slot_service.get_slot(self.slot_id)
            appointment_datetime = slot['start_time'] # Assuming 'start_time' is the datetime object
            
            reminder_message = self.orchestrator.notification_service.format_appointment_reminder(
                patient_name=self.patient_name,
                appointment_date=appointment_datetime
            )
            assert self.patient_name in reminder_message
            assert appointment_datetime.strftime('%d/%m/%Y') in reminder_message
            assert appointment_datetime.strftime('%H:%M') in reminder_message
    
    def test_schedule_insurance_appointment_success(self):
        """Testa o processo completo de agendamento por convênio com sucesso."""
        # Configura os mocks
        with patch('app.services.appointment_orchestrator.create_calendar_event', new_callable=MagicMock) as mock_create_event, \
             patch.object(self.orchestrator.whatsapp_service, 'send_appointment_confirmation', new_callable=MagicMock) as mock_send_confirmation:
            
            # Configura o comportamento dos mocks
            mock_create_event.return_value = {"id": "event123"}
            mock_send_confirmation.return_value = True
            
            # Tenta agendar
            success = self.orchestrator.schedule_appointment(
                patient_id=self.patient_id,
                patient_name=self.patient_name,
                patient_phone=self.patient_phone,
                slot_id=self.slot_id,
                reason=self.reason,
                is_private=False,
                insurance="Unimed",
                insurance_card_url="http://example.com/insurance.pdf",
                id_document_url="http://example.com/id.pdf"
            )
            
            # Verifica se o agendamento foi bem sucedido
            assert success is True
            
            # Verifica se os mocks foram chamados
            mock_create_event.assert_called_once()
            mock_send_confirmation.assert_called_once()
            
            # Verifica se a mensagem de lembrete foi formatada corretamente
            # Get the actual slot details to retrieve the datetime object
            slot = self.orchestrator.scheduling_service.slot_service.get_slot(self.slot_id)
            appointment_datetime = slot['start_time'] # Assuming 'start_time' is the datetime object
            
            reminder_message = self.orchestrator.notification_service.format_appointment_reminder(
                patient_name=self.patient_name,
                appointment_date=appointment_datetime
            )
            assert self.patient_name in reminder_message
            assert appointment_datetime.strftime('%d/%m/%Y') in reminder_message
            assert appointment_datetime.strftime('%H:%M') in reminder_message
    
    def test_schedule_appointment_failure(self):
        """Testa o processo de agendamento com falha."""
        # Configura os mocks
        with patch('app.services.appointment_orchestrator.create_calendar_event', new_callable=MagicMock) as mock_create_event, \
             patch.object(self.orchestrator.whatsapp_service, 'send_appointment_confirmation', new_callable=MagicMock) as mock_send_confirmation:
            
            # Configura o mock para lançar uma exceção
            mock_create_event.side_effect = Exception("Erro ao criar evento")
            
            # Tenta agendar
            success = self.orchestrator.schedule_appointment(
                patient_id=self.patient_id,
                patient_name=self.patient_name,
                patient_phone=self.patient_phone,
                slot_id=self.slot_id,
                reason=self.reason,
                is_private=True,
                id_document_url="http://example.com/id.pdf"
            )
            
            # Verifica se o agendamento falhou
            assert success is False
            
            # Verifica se o WhatsApp não foi chamado
            mock_send_confirmation.assert_not_called()

if __name__ == '__main__':
    pytest.main() 