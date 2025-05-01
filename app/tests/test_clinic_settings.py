from datetime import time
from app.config.clinic_settings import ClinicSettings

def test_working_hours():
    """Testa os horários de funcionamento da clínica"""
    # Segunda, quarta e sexta (tarde)
    assert ClinicSettings.WORKING_HOURS['monday']['start'] == time(14, 0)
    assert ClinicSettings.WORKING_HOURS['monday']['end'] == time(17, 45)
    assert ClinicSettings.WORKING_HOURS['wednesday']['start'] == time(14, 0)
    assert ClinicSettings.WORKING_HOURS['wednesday']['end'] == time(17, 45)
    assert ClinicSettings.WORKING_HOURS['friday']['start'] == time(14, 0)
    assert ClinicSettings.WORKING_HOURS['friday']['end'] == time(17, 45)
    
    # Terça, quinta e sábado (manhã)
    assert ClinicSettings.WORKING_HOURS['tuesday']['start'] == time(8, 30)
    assert ClinicSettings.WORKING_HOURS['tuesday']['end'] == time(12, 15)
    assert ClinicSettings.WORKING_HOURS['thursday']['start'] == time(8, 30)
    assert ClinicSettings.WORKING_HOURS['thursday']['end'] == time(12, 15)
    assert ClinicSettings.WORKING_HOURS['saturday']['start'] == time(8, 30)
    assert ClinicSettings.WORKING_HOURS['saturday']['end'] == time(12, 15)

def test_appointment_settings():
    """Testa as configurações de agendamento"""
    assert ClinicSettings.APPOINTMENT_INTERVAL == 45
    assert ClinicSettings.DEFAULT_APPOINTMENT_DURATION == 45

def test_working_days():
    """Testa os dias de funcionamento"""
    expected_days = ['monday', 'wednesday', 'friday', 'tuesday', 'thursday', 'saturday']
    assert sorted(ClinicSettings.WORKING_DAYS) == sorted(expected_days)

def test_preferred_time_ranges():
    """Testa os intervalos de horário preferenciais"""
    expected_ranges = [
        (time(8, 30), time(12, 15)),   # Manhã: 8h30 às 12h15
        (time(14, 0), time(17, 45))    # Tarde: 14h às 17h45
    ]
    assert ClinicSettings.PREFERRED_TIME_RANGES == expected_ranges

def test_get_available_time_ranges():
    """Testa a geração dos intervalos de horário disponíveis"""
    # Teste para dia da tarde
    ranges = ClinicSettings.get_available_time_ranges('monday')
    assert len(ranges) == 1
    assert ranges[0] == (time(14, 0), time(17, 45))
    
    # Teste para dia da manhã
    ranges = ClinicSettings.get_available_time_ranges('tuesday')
    assert len(ranges) == 1
    assert ranges[0] == (time(8, 30), time(12, 15))
    
    # Teste para dia inválido
    ranges = ClinicSettings.get_available_time_ranges('sunday')
    assert len(ranges) == 0

def test_get_available_slots():
    """Testa a geração dos slots disponíveis"""
    # Teste para dia da tarde
    slots = ClinicSettings.get_available_slots('monday')
    assert len(slots) == 5
    assert slots[0] == time(14, 0)
    assert slots[1] == time(14, 45)
    assert slots[2] == time(15, 30)
    assert slots[3] == time(16, 15)
    assert slots[4] == time(17, 0)
    
    # Teste para dia da manhã
    slots = ClinicSettings.get_available_slots('tuesday')
    assert len(slots) == 5
    assert slots[0] == time(8, 30)
    assert slots[1] == time(9, 15)
    assert slots[2] == time(10, 0)
    assert slots[3] == time(10, 45)
    assert slots[4] == time(11, 30)
    
    # Teste para dia inválido
    slots = ClinicSettings.get_available_slots('sunday')
    assert len(slots) == 0 