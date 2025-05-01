import pytest
from datetime import datetime, timedelta
from app.services.insurance_service import InsuranceService, InsuranceInfo

def test_validate_insurance_provider():
    """Testa a validação de convênios aceitos"""
    service = InsuranceService()
    
    # Testa convênios aceitos
    assert service.validate_insurance_provider("unimed") == True
    assert service.validate_insurance_provider("bradesco") == True
    assert service.validate_insurance_provider("sulamerica") == True
    
    # Testa convênios não aceitos
    assert service.validate_insurance_provider("outro_plano") == False
    assert service.validate_insurance_provider("plano_xyz") == False

def test_verify_insurance_documents():
    """Testa a verificação de documentos do convênio"""
    service = InsuranceService()
    
    # Testa com convênio válido
    valid_date = datetime.now() + timedelta(days=365)
    result = service.verify_insurance_documents(
        provider="unimed",
        card_number="123456789",
        validity=valid_date,
        patient_name="João Silva",
        patient_id="123.456.789-00"
    )
    assert result == True
    
    # Verifica se as informações foram armazenadas
    insurance_info = service.get_insurance_info("123456789")
    assert insurance_info is not None
    assert insurance_info.provider == "unimed"
    assert insurance_info.patient_name == "João Silva"
    
    # Testa com convênio inválido
    result = service.verify_insurance_documents(
        provider="plano_xyz",
        card_number="987654321",
        validity=valid_date,
        patient_name="Maria Santos",
        patient_id="987.654.321-00"
    )
    assert result == False
    assert service.get_insurance_info("987654321") is None

def test_is_insurance_valid():
    """Testa a verificação de validade do convênio"""
    service = InsuranceService()
    
    # Testa convênio válido
    valid_date = datetime.now() + timedelta(days=365)
    service.verify_insurance_documents(
        provider="unimed",
        card_number="123456789",
        validity=valid_date,
        patient_name="João Silva",
        patient_id="123.456.789-00"
    )
    assert service.is_insurance_valid("123456789") == True
    
    # Testa convênio expirado
    expired_date = datetime.now() - timedelta(days=1)
    service.verify_insurance_documents(
        provider="bradesco",
        card_number="987654321",
        validity=expired_date,
        patient_name="Maria Santos",
        patient_id="987.654.321-00"
    )
    assert service.is_insurance_valid("987654321") == False
    
    # Testa convênio não existente
    assert service.is_insurance_valid("000000000") == False 