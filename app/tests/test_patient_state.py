import unittest
from datetime import datetime
from app.models.patient import Patient, PatientType, ConversationState
from app.services.patient_state import PatientStateService

class TestPatientState(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.state_service = PatientStateService()
        self.test_phone = "+5511999999999"

    def test_patient_creation(self):
        """Testa a criação de um novo paciente."""
        patient = Patient(
            id="test123",
            phone=self.test_phone,
            name="João Teste",
            email="joao@teste.com"
        )
        self.assertEqual(patient.name, "João Teste")
        self.assertEqual(patient.conversation_state, ConversationState.INITIAL)
        self.assertIsNone(patient.last_interaction)

    def test_get_or_create_patient(self):
        """Testa obtenção/criação de paciente pelo telefone."""
        # Primeira chamada - deve criar novo paciente
        patient1 = self.state_service.get_or_create_patient(self.test_phone)
        self.assertEqual(patient1.phone, self.test_phone)
        self.assertEqual(patient1.conversation_state, ConversationState.INITIAL)

        # Segunda chamada - deve retornar o mesmo paciente
        patient2 = self.state_service.get_or_create_patient(self.test_phone)
        self.assertEqual(patient1, patient2)

    def test_update_patient_info(self):
        """Testa atualização de informações do paciente."""
        patient = self.state_service.get_or_create_patient(self.test_phone)
        
        updated_patient = self.state_service.update_patient_info(
            patient_id=patient.id,
            name="Maria Teste",
            email="maria@teste.com",
            patient_type=PatientType.INSURANCE,
            insurance_id="unimed-basic",
            insurance_card_number="12345"
        )

        self.assertEqual(updated_patient.name, "Maria Teste")
        self.assertEqual(updated_patient.email, "maria@teste.com")
        self.assertEqual(updated_patient.patient_type, PatientType.INSURANCE)
        self.assertEqual(updated_patient.insurance_id, "unimed-basic")

    def test_conversation_state_transitions(self):
        """Testa transições de estado da conversa."""
        patient = self.state_service.get_or_create_patient(self.test_phone)
        
        # Testa transição para coleta de informações
        self.state_service.update_conversation_state(
            patient.id,
            ConversationState.COLLECTING_INFO
        )
        self.assertEqual(
            patient.conversation_state,
            ConversationState.COLLECTING_INFO
        )
        self.assertIsNotNone(patient.last_interaction)

        # Testa transição para validação de convênio
        self.state_service.update_conversation_state(
            patient.id,
            ConversationState.VALIDATING_INSURANCE
        )
        self.assertEqual(
            patient.conversation_state,
            ConversationState.VALIDATING_INSURANCE
        )

    def test_context_management(self):
        """Testa gerenciamento do contexto da conversa."""
        patient = self.state_service.get_or_create_patient(self.test_phone)
        
        # Adiciona informações ao contexto
        patient.add_context("preferred_time", "manhã")
        patient.add_context("symptoms", ["dor de cabeça", "insônia"])
        
        self.assertEqual(patient.context["preferred_time"], "manhã")
        self.assertEqual(len(patient.context["symptoms"]), 2)
        
        # Limpa o contexto
        patient.clear_context()
        self.assertEqual(len(patient.context), 0)

    def test_appointment_history(self):
        """Testa gerenciamento do histórico de consultas."""
        patient = self.state_service.get_or_create_patient(self.test_phone)
        
        # Adiciona consultas ao histórico
        now = datetime.now()
        patient.add_appointment(now)
        
        self.assertEqual(len(patient.appointment_history), 1)
        self.assertEqual(patient.get_last_appointment(), now)

    def test_get_next_question(self):
        """Testa a lógica de próximas perguntas."""
        patient = self.state_service.get_or_create_patient(self.test_phone)
        
        # Paciente sem nome - deve perguntar o nome
        question = self.state_service.get_next_question(patient)
        self.assertIn("nome", question.lower())
        
        # Atualiza nome e verifica próxima pergunta
        patient.name = "Test Patient"
        question = self.state_service.get_next_question(patient)
        self.assertIn("particular", question.lower())
        self.assertIn("convênio", question.lower())

        # Define tipo de paciente e verifica próxima pergunta
        patient.patient_type = PatientType.INSURANCE
        question = self.state_service.get_next_question(patient)
        self.assertIn("convênio", question.lower())

if __name__ == '__main__':
    unittest.main() 