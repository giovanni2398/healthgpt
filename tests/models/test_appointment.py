from datetime import datetime
import pytest
from app.models.appointment import Appointment

def test_appointment_creation():
    """Testa a criação de um agendamento com todos os campos."""
    now = datetime.now()
    appointment = Appointment(
        id="123",
        patient_id="456",
        name="João Silva",
        start_time=now,
        end_time=now,
        reason="Consulta nutricional",
        is_private=True,
        insurance=None,
        insurance_card_url=None,
        id_document_url=None
    )
    
    assert appointment.id == "123"
    assert appointment.patient_id == "456"
    assert appointment.name == "João Silva"
    assert appointment.start_time == now
    assert appointment.end_time == now
    assert appointment.reason == "Consulta nutricional"
    assert appointment.is_private == True
    assert appointment.insurance is None
    assert appointment.insurance_card_url is None
    assert appointment.id_document_url is None
    assert appointment.status == "scheduled"
    assert isinstance(appointment.created_at, datetime)
    assert isinstance(appointment.updated_at, datetime)

def test_appointment_with_insurance():
    """Testa a criação de um agendamento com convênio."""
    now = datetime.now()
    appointment = Appointment(
        id="456",
        patient_id="789",
        name="Maria Santos",
        start_time=now,
        end_time=now,
        reason="Consulta nutricional",
        is_private=False,
        insurance="Unimed",
        insurance_card_url="https://example.com/card.jpg",
        id_document_url="https://example.com/id.jpg"
    )
    
    assert appointment.is_private == False
    assert appointment.insurance == "Unimed"
    assert appointment.insurance_card_url == "https://example.com/card.jpg"
    assert appointment.id_document_url == "https://example.com/id.jpg"

def test_appointment_to_dict():
    """Testa a conversão do agendamento para dicionário."""
    now = datetime.now()
    appointment = Appointment(
        id="789",
        patient_id="012",
        name="Pedro Oliveira",
        start_time=now,
        end_time=now,
        reason="Consulta nutricional",
        is_private=True
    )
    
    appointment_dict = appointment.to_dict()
    
    assert appointment_dict["id"] == "789"
    assert appointment_dict["patient_id"] == "012"
    assert appointment_dict["name"] == "Pedro Oliveira"
    assert appointment_dict["start_time"] == now.isoformat()
    assert appointment_dict["end_time"] == now.isoformat()
    assert appointment_dict["reason"] == "Consulta nutricional"
    assert appointment_dict["is_private"] == True
    assert appointment_dict["insurance"] is None
    assert appointment_dict["insurance_card_url"] is None
    assert appointment_dict["id_document_url"] is None
    assert appointment_dict["status"] == "scheduled"
    assert isinstance(appointment_dict["created_at"], str)
    assert isinstance(appointment_dict["updated_at"], str) 