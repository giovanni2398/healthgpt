from datetime import datetime, timedelta
import unittest

from app.services.scheduling_service import SchedulingService
from app.models.slot import TimeSlot

class TestSchedulingService(unittest.TestCase):
    def setUp(self):
        """Configura o ambiente de teste."""
        self.scheduling_service = SchedulingService()
        self.patient_id = "123"
        self.reason = "Consulta de rotina"
        
        # Cria alguns slots para teste
        now = datetime.now()
        self.slot1 = self.scheduling_service.slot_service.create_slot(
            start_time=now + timedelta(days=1, hours=10),
            end_time=now + timedelta(days=1, hours=10, minutes=30)
        )
        self.slot2 = self.scheduling_service.slot_service.create_slot(
            start_time=now + timedelta(days=1, hours=11),
            end_time=now + timedelta(days=1, hours=11, minutes=30)
        )
    
    def test_create_appointment(self):
        """Testa a criação de um agendamento."""
        # Tenta criar um agendamento
        appointment = self.scheduling_service.create_appointment(
            patient_id=self.patient_id,
            slot_id=self.slot1.id,
            reason=self.reason
        )
        
        # Verifica se o agendamento foi criado corretamente
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.patient_id, self.patient_id)
        self.assertEqual(appointment.slot_id, self.slot1.id)
        self.assertEqual(appointment.reason, self.reason)
        
        # Verifica se o slot foi marcado como ocupado
        slot = self.scheduling_service.slot_service.get_slot(self.slot1.id)
        self.assertFalse(slot.is_available)
    
    def test_get_patient_appointments(self):
        """Testa a busca de agendamentos de um paciente."""
        # Cria um agendamento
        appointment = self.scheduling_service.create_appointment(
            patient_id=self.patient_id,
            slot_id=self.slot1.id,
            reason=self.reason
        )
        
        # Busca os agendamentos do paciente
        appointments = self.scheduling_service.get_patient_appointments(self.patient_id)
        
        # Verifica se o agendamento foi encontrado
        self.assertEqual(len(appointments), 1)
        self.assertEqual(appointments[0].id, appointment.id)
    
    def test_get_available_slots(self):
        """Testa a busca de slots disponíveis."""
        # Cria um agendamento ocupando um slot
        self.scheduling_service.create_appointment(
            patient_id=self.patient_id,
            slot_id=self.slot1.id,
            reason=self.reason
        )
        
        # Busca slots disponíveis
        start_date = datetime.now()
        end_date = start_date + timedelta(days=2)
        available_slots = self.scheduling_service.get_available_slots(start_date, end_date)
        
        # Verifica se apenas o slot2 está disponível
        self.assertEqual(len(available_slots), 1)
        self.assertEqual(available_slots[0].id, self.slot2.id)

if __name__ == '__main__':
    unittest.main() 