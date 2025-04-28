import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from app.services.scheduling_service import SchedulingService
from app.services.slot_service import SlotService

class TestSchedulingService:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Configura o ambiente de teste."""
        self.slot_service = SlotService()
        self.scheduling_service = SchedulingService(slot_service=self.slot_service)
        
        # Dados de teste
        self.patient_id = "123"
        self.patient_name = "João Silva"
        self.reason = "Consulta de rotina"
        
        # Cria slots para teste
        now = datetime.now()
        self.slot1_id = self.slot_service.create_slot(
            start_time=now + timedelta(days=1, hours=10),
            end_time=now + timedelta(days=1, hours=11)
        )
        self.slot2_id = self.slot_service.create_slot(
            start_time=now + timedelta(days=1, hours=14),
            end_time=now + timedelta(days=1, hours=15)
        )
    
    def test_create_private_appointment(self):
        """Testa a criação de um agendamento particular."""
        # Tenta criar um agendamento
        appointment = self.scheduling_service.create_appointment(
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            slot_id=self.slot1_id,
            reason=self.reason,
            is_private=True,
            id_document_url="http://example.com/id.pdf"
        )
        
        # Verifica se o agendamento foi criado corretamente
        assert appointment is not None
        assert appointment.patient_id == self.patient_id
        assert appointment.name == self.patient_name
        assert appointment.reason == self.reason
        assert appointment.is_private is True
        assert appointment.id_document_url == "http://example.com/id.pdf"
        
        # Verifica se o slot foi marcado como indisponível
        slot = self.slot_service.get_slot(self.slot1_id)
        assert slot["is_available"] is False
    
    def test_create_insurance_appointment(self):
        """Testa a criação de um agendamento por convênio."""
        # Tenta criar um agendamento
        appointment = self.scheduling_service.create_appointment(
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            slot_id=self.slot1_id,
            reason=self.reason,
            is_private=False,
            insurance="Unimed",
            insurance_card_url="http://example.com/insurance.pdf",
            id_document_url="http://example.com/id.pdf"
        )
        
        # Verifica se o agendamento foi criado corretamente
        assert appointment is not None
        assert appointment.patient_id == self.patient_id
        assert appointment.name == self.patient_name
        assert appointment.reason == self.reason
        assert appointment.is_private is False
        assert appointment.insurance == "Unimed"
        assert appointment.insurance_card_url == "http://example.com/insurance.pdf"
        assert appointment.id_document_url == "http://example.com/id.pdf"
        
        # Verifica se o slot foi marcado como indisponível
        slot = self.slot_service.get_slot(self.slot1_id)
        assert slot["is_available"] is False
    
    def test_get_patient_appointments(self):
        """Testa a busca de agendamentos de um paciente."""
        # Cria um agendamento
        appointment = self.scheduling_service.create_appointment(
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            slot_id=self.slot1_id,
            reason=self.reason,
            is_private=True,
            id_document_url="http://example.com/id.pdf"
        )
        
        # Busca os agendamentos do paciente
        appointments = self.scheduling_service.get_patient_appointments(self.patient_id)
        
        # Verifica se o agendamento foi encontrado
        assert len(appointments) == 1
        assert appointments[0].id == appointment.id
    
    def test_get_available_slots(self):
        """Testa a busca de slots disponíveis."""
        # Cria um agendamento ocupando um slot
        self.scheduling_service.create_appointment(
            patient_id=self.patient_id,
            patient_name=self.patient_name,
            slot_id=self.slot1_id,
            reason=self.reason,
            is_private=True,
            id_document_url="http://example.com/id.pdf"
        )
        
        # Busca os slots disponíveis
        now = datetime.now()
        available_slots = self.scheduling_service.get_available_slots(
            now,
            now + timedelta(days=2)
        )
        
        # Verifica se apenas o slot2 está disponível
        assert len(available_slots) == 1
        assert available_slots[0]["id"] == self.slot2_id 