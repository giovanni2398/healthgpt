import pytest
from datetime import datetime, timedelta

from app.services.insurance_service import InsuranceService
from app.config.insurance_plans import ACCEPTED_INSURANCE_PLANS
from app.models.insurance import InsuranceValidation, InsurancePlan


def test_get_accepted_plans():
    service = InsuranceService()
    plans = service.get_accepted_plans()
    # Deve retornar todos os planos configurados
    assert isinstance(plans, list)
    assert len(plans) == len(ACCEPTED_INSURANCE_PLANS)
    ids = {plan.id for plan in plans}
    assert set(ACCEPTED_INSURANCE_PLANS.keys()) == ids


def test_get_plan_by_name_case_insensitive_and_not_found():
    service = InsuranceService()
    plan = service.get_plan_by_name("Unimed")
    assert isinstance(plan, InsurancePlan)
    assert plan.id == "unimed"
    # Busca insensível a maiúsculas
    plan2 = service.get_plan_by_name("AMIL")
    assert plan2.id == "amil"
    # Plano não existente retorna None
    assert service.get_plan_by_name("invalid") is None


def test_register_insurance_and_get_insurance():
    service = InsuranceService()
    val = service.register_insurance("patient1", "unimed")
    assert isinstance(val, InsuranceValidation)
    assert val.insurance_id == "unimed"
    assert val.patient_id == "patient1"
    assert not val.documents_received
    # get_insurance deve retornar o mesmo objeto
    fetched = service.get_insurance("patient1", "unimed")
    assert fetched == val

def test_mark_documents_received_and_can_schedule():
    service = InsuranceService()
    # Registrar plano e marcar documentos
    service.register_insurance("p1", "unimed")
    val = service.mark_documents_received("p1", "unimed")
    assert val.documents_received
    # Agora pode agendar
    assert service.can_schedule_appointment("p1", "unimed")


def test_mark_documents_received_without_register_raises():
    service = InsuranceService()
    with pytest.raises(ValueError):
        service.mark_documents_received("p2", "unimed")


def test_can_schedule_without_register():
    service = InsuranceService()
    assert not service.can_schedule_appointment("p3", "amil")


# Removed test for format_validation_message per updated requirements 