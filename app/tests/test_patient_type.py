import unittest
from app.models.patient import Patient, PatientType, ConversationState
from app.services.patient_state import PatientStateService
from app.services.patient_type_service import PatientTypeService

class TestPatientTypeService(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.patient_state_service = PatientStateService()
        self.test_patient = self.patient_state_service.get_or_create_patient("+5511999999999")
        self.test_patient.name = "João Teste"
        self.test_patient.patient_type = PatientType.UNDEFINED
        self.patient_type_service = PatientTypeService(self.patient_state_service)

    def test_identify_patient_type_private(self):
        """Testa identificação de paciente particular."""
        # Testa diferentes variações de "particular"
        messages = [
            "sou particular",
            "quero ser particular",
            "vou pagar particular",
            "particular mesmo"
        ]
        
        for message in messages:
            identified_type = self.patient_type_service.identify_patient_type(
                message,
                self.test_patient
            )
            self.assertEqual(identified_type, PatientType.PRIVATE)

    def test_identify_patient_type_insurance(self):
        """Testa identificação de paciente com convênio."""
        # Testa diferentes variações de "convênio"
        messages = [
            "tenho convênio",
            "sou do unimed",
            "tenho plano da amil",
            "meu convênio é bradesco"
        ]
        
        for message in messages:
            identified_type = self.patient_type_service.identify_patient_type(
                message,
                self.test_patient
            )
            self.assertEqual(identified_type, PatientType.INSURANCE)

    def test_identify_patient_type_unknown(self):
        """Testa mensagens que não identificam o tipo."""
        messages = [
            "bom dia",
            "quero marcar consulta",
            "preciso de ajuda"
        ]
        
        for message in messages:
            identified_type = self.patient_type_service.identify_patient_type(
                message,
                self.test_patient
            )
            self.assertIsNone(identified_type)

    def test_update_patient_type(self):
        """Testa atualização do tipo de paciente."""
        # Testa mudança para particular
        updated_patient = self.patient_type_service.update_patient_type(
            self.test_patient,
            PatientType.PRIVATE
        )
        self.assertEqual(updated_patient.patient_type, PatientType.PRIVATE)
        self.assertEqual(
            updated_patient.conversation_state,
            ConversationState.SCHEDULING
        )

        # Testa mudança para convênio
        updated_patient = self.patient_type_service.update_patient_type(
            self.test_patient,
            PatientType.INSURANCE
        )
        self.assertEqual(updated_patient.patient_type, PatientType.INSURANCE)
        self.assertEqual(
            updated_patient.conversation_state,
            ConversationState.VALIDATING_INSURANCE
        )

    def test_handle_patient_response(self):
        """Testa o processamento completo da resposta do paciente."""
        # Testa resposta de particular
        response = self.patient_type_service.handle_patient_response(
            "sou particular",
            self.test_patient
        )
        self.assertTrue(response["success"])
        self.assertEqual(
            response["patient"].patient_type,
            PatientType.PRIVATE
        )
        self.assertIn("pagar", response["next_question"].lower())

        # Reseta o paciente para o próximo teste
        self.test_patient.patient_type = PatientType.UNDEFINED

        # Testa resposta de convênio
        response = self.patient_type_service.handle_patient_response(
            "tenho unimed",
            self.test_patient
        )
        self.assertTrue(response["success"])
        self.assertEqual(
            response["patient"].patient_type,
            PatientType.INSURANCE
        )
        self.assertIn("convênio", response["next_question"])

        # Reseta o paciente para o próximo teste
        self.test_patient.patient_type = PatientType.UNDEFINED

        # Testa resposta não reconhecida
        response = self.patient_type_service.handle_patient_response(
            "bom dia",
            self.test_patient
        )
        self.assertFalse(response["success"])
        self.assertIn("particular", response["next_question"].lower())
        self.assertIn("convênio", response["next_question"].lower())

if __name__ == '__main__':
    unittest.main() 