import unittest
from app.models.insurance import InsurancePlan, InsuranceValidation
from app.services.insurance_service import InsuranceService

class TestInsuranceValidation(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.insurance_service = InsuranceService()
        self.test_patient_id = "test123"

    def test_insurance_plan_creation(self):
        """Testa a criação de um plano de convênio."""
        plan = InsurancePlan(
            id="test-plan",
            name="Plano Teste"
        )
        self.assertEqual(plan.name, "Plano Teste")

    def test_get_accepted_plans(self):
        """Testa a listagem de planos aceitos."""
        plans = self.insurance_service.get_accepted_plans()
        self.assertTrue(len(plans) > 0)

    def test_register_insurance_success(self):
        """Testa registro de convênio."""
        validation = self.insurance_service.register_insurance(
            self.test_patient_id,
            "unimed"
        )
        self.assertEqual(validation.insurance_id, "unimed")
        self.assertFalse(validation.documents_received)

    def test_mark_documents_received(self):
        """Testa marcação de documentos recebidos."""
        # Primeiro registra o convênio
        self.insurance_service.register_insurance(
            self.test_patient_id,
            "unimed"
        )

        # Marca documentos como recebidos
        validation = self.insurance_service.mark_documents_received(
            self.test_patient_id,
            "unimed"
        )
        self.assertTrue(validation.documents_received)

    def test_mark_documents_received_invalid(self):
        """Testa marcação de documentos para convênio não registrado."""
        with self.assertRaises(ValueError):
            self.insurance_service.mark_documents_received(
                self.test_patient_id,
                "unimed"
            )

    def test_can_schedule_appointment(self):
        """Testa verificação de permissão para agendamento."""
        # Registra convênio
        self.insurance_service.register_insurance(
            self.test_patient_id,
            "unimed"
        )

        # Antes de receber documentos
        self.assertFalse(
            self.insurance_service.can_schedule_appointment(
                self.test_patient_id,
                "unimed"
            )
        )

        # Marca documentos como recebidos
        self.insurance_service.mark_documents_received(
            self.test_patient_id,
            "unimed"
        )

        # Após receber documentos
        self.assertTrue(
            self.insurance_service.can_schedule_appointment(
                self.test_patient_id,
                "unimed"
            )
        )

    def test_can_schedule_appointment_invalid(self):
        """Testa verificação de permissão para convênio inválido."""
        self.assertFalse(
            self.insurance_service.can_schedule_appointment(
                self.test_patient_id,
                "invalid-plan"
            )
        )

    def test_invalid_insurance_id(self):
        """Testa registro com ID de convênio inválido."""
        with self.assertRaises(ValueError):
            self.insurance_service.register_insurance(
                self.test_patient_id,
                "invalid-plan"
            )

    def test_get_plan_by_name(self):
        """Testa busca de plano pelo nome."""
        # Testa busca exata
        plan = self.insurance_service.get_plan_by_name("Unimed")
        self.assertIsNotNone(plan)
        self.assertEqual(plan.id, "unimed")

        # Testa busca inexistente
        plan = self.insurance_service.get_plan_by_name("Plano Inexistente")
        self.assertIsNone(plan)

if __name__ == '__main__':
    unittest.main() 