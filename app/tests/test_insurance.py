import unittest
from datetime import datetime, timedelta
from app.models.insurance import InsurancePlan, InsuranceValidation
from app.services.insurance_service import InsuranceService

class TestInsuranceValidation(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.insurance_service = InsuranceService()
        self.test_patient_id = "test123"
        self.test_card_number = "12345"

    def test_insurance_plan_creation(self):
        """Testa a criação de um plano de convênio."""
        plan = InsurancePlan(
            id="test-plan",
            name="Plano Teste",
            provider="Provedor Teste",
            coverage_type="basic",
            waiting_period_days=15,
            active=True
        )
        self.assertEqual(plan.name, "Plano Teste")
        self.assertEqual(plan.waiting_period_days, 15)
        self.assertTrue(plan.active)

    def test_get_accepted_plans(self):
        """Testa a listagem de planos aceitos."""
        plans = self.insurance_service.get_accepted_plans()
        self.assertTrue(len(plans) > 0)
        self.assertTrue(all(plan.active for plan in plans))

    def test_validate_insurance_success(self):
        """Testa validação bem-sucedida de convênio."""
        # Testa com plano Amil Premium (sem carência)
        validation = self.insurance_service.validate_insurance(
            self.test_patient_id,
            "amil-premium",
            self.test_card_number
        )
        self.assertTrue(validation.is_valid())
        self.assertEqual(validation.status, "active")
        self.assertIsNone(validation.waiting_period_ends)

    def test_validate_insurance_with_waiting_period(self):
        """Testa validação de convênio com período de carência."""
        # Testa com plano Unimed Basic (30 dias de carência)
        validation = self.insurance_service.validate_insurance(
            self.test_patient_id,
            "unimed-basic",
            self.test_card_number
        )
        self.assertFalse(validation.is_valid())
        self.assertEqual(validation.status, "waiting_period")
        self.assertIsNotNone(validation.waiting_period_ends)

    def test_invalid_insurance_id(self):
        """Testa validação com ID de convênio inválido."""
        with self.assertRaises(ValueError):
            self.insurance_service.validate_insurance(
                self.test_patient_id,
                "invalid-plan",
                self.test_card_number
            )

    def test_validation_message_formatting(self):
        """Testa formatação das mensagens de validação."""
        validation = self.insurance_service.validate_insurance(
            self.test_patient_id,
            "amil-premium",
            self.test_card_number
        )
        message = self.insurance_service.format_validation_message(validation)
        self.assertIn("Amil Premium", message)
        self.assertIn("✅", message)  # Deve conter emoji de sucesso

    def test_expired_insurance(self):
        """Testa validação de convênio expirado."""
        validation = InsuranceValidation(
            insurance_id="test-plan",
            patient_id=self.test_patient_id,
            card_number=self.test_card_number,
            valid_until=datetime.now() - timedelta(days=1),  # Data no passado
            status="active"
        )
        self.assertFalse(validation.is_valid())
        self.assertIn("vencido", validation.get_validation_message())

if __name__ == '__main__':
    unittest.main() 