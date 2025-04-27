import unittest
from datetime import datetime
from app.models.patient import Patient, PatientType, ConversationState, InsuranceStatus
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
        """Testa criação e recuperação de paciente."""
        patient = self.state_service.get_or_create_patient(self.test_phone)
        self.assertEqual(patient.phone, self.test_phone)
        self.assertEqual(patient.conversation_state, ConversationState.INITIAL)

    def test_update_patient_info(self):
        """Testa atualização de informações do paciente."""
        patient = self.state_service.get_or_create_patient(self.test_phone)
        
        updated_patient = self.state_service.update_patient_info(
            patient_id=patient.id,
            name="Maria Teste",
            email="maria@teste.com",
            patient_type=PatientType.INSURANCE,
            insurance_id="unimed"
        )

        self.assertEqual(updated_patient.name, "Maria Teste")
        self.assertEqual(updated_patient.email, "maria@teste.com")
        self.assertEqual(updated_patient.patient_type, PatientType.INSURANCE)
        self.assertEqual(updated_patient.insurance_id, "unimed")
        self.assertEqual(updated_patient.insurance_status, InsuranceStatus.WAITING_DOCS)

    def test_update_patient_info_invalid_insurance(self):
        """Testa atualização com convênio inválido."""
        patient = self.state_service.get_or_create_patient(self.test_phone)
        
        updated_patient = self.state_service.update_patient_info(
            patient_id=patient.id,
            insurance_id="invalid-insurance"
        )

        self.assertEqual(updated_patient.insurance_status, InsuranceStatus.INVALID)

    def test_mark_insurance_documents_received(self):
        """Testa marcação de documentos recebidos."""
        # Primeiro registra o paciente com convênio
        patient = self.state_service.get_or_create_patient(self.test_phone)
        patient = self.state_service.update_patient_info(
            patient_id=patient.id,
            insurance_id="unimed"
        )

        # Marca documentos como recebidos
        updated_patient = self.state_service.mark_insurance_documents_received(
            patient_id=patient.id,
            insurance_id="unimed"
        )

        self.assertEqual(updated_patient.insurance_status, InsuranceStatus.VALIDATED)
        self.assertEqual(updated_patient.conversation_state, ConversationState.SCHEDULING)

    def test_mark_insurance_documents_received_invalid(self):
        """Testa marcação de documentos com convênio inválido."""
        patient = self.state_service.get_or_create_patient(self.test_phone)
        
        with self.assertRaises(ValueError):
            self.state_service.mark_insurance_documents_received(
                patient_id=patient.id,
                insurance_id="unimed"
            )

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

        # Define convênio e verifica próxima pergunta
        patient.insurance_id = "unimed"
        patient.insurance_status = InsuranceStatus.WAITING_DOCS
        question = self.state_service.get_next_question(patient)
        self.assertIn("documento", question.lower())
        self.assertIn("carteirinha", question.lower())

if __name__ == '__main__':
    unittest.main() 