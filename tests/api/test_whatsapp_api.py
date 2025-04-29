import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import status, BackgroundTasks

# Import the main app and router
# Assuming your main app instance is in 'app.main' and named 'app'
# Adjust the import path if your structure is different
from app.main import app 
from app.api.whatsapp import router as whatsapp_router, VERIFY_TOKEN, process_whatsapp_message 
from app.services.conversation_state_service import ConversationStateService
from app.services.whatsapp_service import WhatsAppService
from app.services.scheduling_service import SchedulingService
from app.services.appointment_orchestrator import AppointmentOrchestrator

# Include the WhatsApp router in the TestClient app instance
app.include_router(whatsapp_router, prefix="/whatsapp_test") # Use a prefix to avoid conflicts if needed

client = TestClient(app)

# --- Fixtures and Mocks ---

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """ Mocks environment variables needed by the API. """
    monkeypatch.setenv("VERIFY_TOKEN", "test_verify_token")
    monkeypatch.setenv("GOOGLE_SCHEDULES_LINK", "http://fake.google.link")
    # Add other env vars if needed

@pytest.fixture
def mock_state_service():
    """ Mocks ConversationStateService. """
    with patch('app.api.whatsapp.ConversationStateService', autospec=True) as mock:
        instance = mock.return_value
        instance.get_state = MagicMock(return_value=None) # Default: NEW state
        instance.save_state = MagicMock()
        yield instance

@pytest.fixture
def mock_whatsapp_service():
    """ Mocks WhatsAppService. """
    with patch('app.api.whatsapp.WhatsAppService', autospec=True) as mock:
        instance = mock.return_value
        instance.send_message = AsyncMock() # Needs to be AsyncMock if called with await
        yield instance
        
@pytest.fixture
def mock_scheduling_service():
    """ Mocks SchedulingService. """
    with patch('app.api.whatsapp.SchedulingService', autospec=True) as mock:
        instance = mock.return_value
        instance.get_available_slots = MagicMock(return_value=[]) # Default: No slots
        instance.reserve_slot = MagicMock(return_value={"success": False, "error": "Mock reservation failed"}) # Default: Fail
        yield instance

@pytest.fixture
def mock_orchestrator_service():
    """ Mocks AppointmentOrchestrator. """
    with patch('app.api.whatsapp.AppointmentOrchestrator', autospec=True) as mock:
        instance = mock.return_value
        instance.validate_insurance = MagicMock(return_value=False) # Default: Invalid insurance
        instance.ACCEPTED_INSURANCES = ["GoodHealth", "SecurePlan"] # Example accepted
        yield instance
        
@pytest.fixture
def mock_background_tasks():
    """ Mocks BackgroundTasks to run tasks immediately. """
    # This allows testing the background task logic synchronously
    class ImmediateBackgroundTasks(BackgroundTasks):
        def add_task(self, func, *args, **kwargs) -> None:
            # Run the task immediately instead of in the background
            import asyncio
            try:
                # Check if the function is async
                if asyncio.iscoroutinefunction(func):
                    asyncio.run(func(*args, **kwargs))
                else:
                    func(*args, **kwargs)
            except Exception as e:
                 print(f"Error running background task {func.__name__}: {e}")
                 raise # Re-raise the exception to fail the test

    with patch('app.api.whatsapp.BackgroundTasks', new=ImmediateBackgroundTasks) as mock:
         yield mock

# --- Helper Function to Create Payload ---

def create_whatsapp_payload(phone_number: str, message_text: str) -> dict:
    """ Creates a simplified mock WhatsApp incoming message payload. """
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "PHONE_NUMBER",
                        "phone_number_id": "PHONE_NUMBER_ID"
                    },
                    "contacts": [{"profile": {"name": "User Name"}, "wa_id": phone_number}],
                    "messages": [{
                        "from": phone_number,
                        "id": "MSG_ID",
                        "timestamp": "TIMESTAMP",
                        "text": {"body": message_text},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }

# --- Test Cases Start Here ---

# TODO: Add test cases for GET /webhook verification
# TODO: Add test cases for POST /webhook covering different states

@pytest.mark.asyncio
async def test_webhook_verification_success(mock_env_vars):
    """ Test successful webhook verification. """
    # Patch the VERIFY_TOKEN specifically for this test's scope
    with patch('app.api.whatsapp.VERIFY_TOKEN', 'test_verify_token'):
        response = client.get(
            "/whatsapp_test/webhook", 
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "challenge_code",
                "hub.verify_token": "test_verify_token"
            }
        )
    assert response.status_code == status.HTTP_200_OK
    assert response.text == "challenge_code"

@pytest.mark.asyncio
async def test_webhook_verification_failure_token(mock_env_vars):
    """ Test webhook verification failure due to wrong token. """
    response = client.get(
        "/whatsapp_test/webhook", 
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "challenge_code",
            "hub.verify_token": "wrong_token"
        }
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_webhook_verification_failure_missing_params(mock_env_vars):
    """ Test webhook verification failure due to missing parameters. """
    response = client.get(
        "/whatsapp_test/webhook", 
        params={"hub.mode": "subscribe"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_post_webhook_new_contact(
    mock_state_service,
    mock_whatsapp_service,
    mock_background_tasks # Include mocks needed by process_whatsapp_message
):
    """ Test receiving the first message from a new contact. """
    phone_number = "1234567890"
    payload = create_whatsapp_payload(phone_number, "Oi")
    
    # Ensure state service returns None for this user initially
    mock_state_service.get_state.return_value = None 
    
    # Patch the link specifically for this test's scope
    with patch('app.api.whatsapp.GOOGLE_SCHEDULES_LINK', 'http://fake.google.link'):
        response = client.post("/whatsapp_test/webhook", json=payload)
    
    # Assert endpoint returns OK immediately
    assert response.status_code == status.HTTP_200_OK
    
    # Assert background task ran and services were called correctly
    mock_state_service.get_state.assert_called_once_with(phone_number)
    
    # Check the welcome message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Bem-vindo(a)" in call_args[1]
    assert "http://fake.google.link" in call_args[1]
    assert "Como gostaria de prosseguir?" in call_args[1]
    
    # Check the state was saved correctly
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "AWAITING_INITIAL_CHOICE", 
        {}
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_initial_choice_chat(
    mock_state_service,
    mock_whatsapp_service,
    mock_background_tasks
):
    """ Test user choosing to chat in AWAITING_INITIAL_CHOICE state. """
    phone_number = "1234567891"
    message_text = "quero agendar por aqui"
    payload = create_whatsapp_payload(phone_number, message_text)
    
    # Set initial state
    mock_state_service.get_state.return_value = {"state": "AWAITING_INITIAL_CHOICE", "context": {}}
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    
    # Check the correct follow-up message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Ok, vamos agendar por aqui" in call_args[1]
    assert "particular ou por convênio?" in call_args[1]
    
    # Check the state transition
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "AWAITING_TYPE", 
        {}
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_initial_choice_link(
    mock_state_service,
    mock_whatsapp_service,
    mock_background_tasks
):
    """ Test user asking for the link in AWAITING_INITIAL_CHOICE state. """
    phone_number = "1234567892"
    message_text = "me manda o link"
    payload = create_whatsapp_payload(phone_number, message_text)
    
    # Set initial state
    mock_state_service.get_state.return_value = {"state": "AWAITING_INITIAL_CHOICE", "context": {}}
    
    # Patch the link specifically for this test's scope
    with patch('app.api.whatsapp.GOOGLE_SCHEDULES_LINK', 'http://fake.google.link'):
        response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    
    # Check the correct link message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Ok! Use este link para agendar:" in call_args[1]
    assert "http://fake.google.link" in call_args[1]
    
    # Check the state transition to REDIRECTED_TO_LINK
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "REDIRECTED_TO_LINK", 
        {"link_sent": True}
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_type_private(
    mock_state_service,
    mock_whatsapp_service,
    mock_background_tasks
):
    """ Test user choosing private consultation in AWAITING_TYPE state. """
    phone_number = "1234567893"
    message_text = "particular"
    initial_context = {}
    payload = create_whatsapp_payload(phone_number, message_text)
    
    # Set initial state
    mock_state_service.get_state.return_value = {"state": "AWAITING_TYPE", "context": initial_context}
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    
    # Check the private info message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Entendido. O atendimento particular funciona assim:" in call_args[1]
    assert "Um de nossos atendentes entrará em contato" in call_args[1]
    
    # Check the state transition to HUMAN_TAKEOVER
    expected_context = {"is_private": True} # Context should be updated
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "HUMAN_TAKEOVER", 
        expected_context
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_type_insurance(
    mock_state_service,
    mock_whatsapp_service,
    mock_background_tasks
):
    """ Test user choosing insurance consultation in AWAITING_TYPE state. """
    phone_number = "1234567894"
    message_text = "convenio"
    initial_context = {}
    payload = create_whatsapp_payload(phone_number, message_text)
    
    # Set initial state
    mock_state_service.get_state.return_value = {"state": "AWAITING_TYPE", "context": initial_context}
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    
    # Check the insurance name prompt was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Ok, qual o nome do seu convênio/plano de saúde?" in call_args[1]
    
    # Check the state transition
    expected_context = {"is_private": False}
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "AWAITING_INSURANCE_NAME", 
        expected_context
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_insurance_name_valid(
    mock_state_service,
    mock_whatsapp_service,
    mock_orchestrator_service, # Need orchestrator for validation
    mock_background_tasks
):
    """ Test user providing a valid insurance name. """
    phone_number = "1234567895"
    insurance_name = "GoodHealth"
    initial_context = {"is_private": False}
    payload = create_whatsapp_payload(phone_number, insurance_name)
    
    # Set initial state and mock validation result
    mock_state_service.get_state.return_value = {"state": "AWAITING_INSURANCE_NAME", "context": initial_context}
    mock_orchestrator_service.validate_insurance.return_value = True
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    mock_orchestrator_service.validate_insurance.assert_called_once_with(insurance_name)
    
    # Check the document request message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert f"Perfeito, atendemos {insurance_name}" in call_args[1]
    assert "envie aqui no chat fotos legíveis" in call_args[1]
    assert "documento de identidade" in call_args[1]
    assert "carteirinha do convênio" in call_args[1]
    
    # Check the state transition
    expected_context = {"is_private": False, "insurance_name": insurance_name}
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "AWAITING_DOCS_INSURANCE", 
        expected_context
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_insurance_name_invalid(
    mock_state_service,
    mock_whatsapp_service,
    mock_orchestrator_service, # Need orchestrator for validation
    mock_background_tasks
):
    """ Test user providing an invalid insurance name. """
    phone_number = "1234567896"
    insurance_name = "BadHealth"
    initial_context = {"is_private": False} 
    payload = create_whatsapp_payload(phone_number, insurance_name)
    
    # Set initial state and mock validation result
    mock_state_service.get_state.return_value = {"state": "AWAITING_INSURANCE_NAME", "context": initial_context}
    mock_orchestrator_service.validate_insurance.return_value = False # Invalid
    accepted_insurances_str = ", ".join(mock_orchestrator_service.ACCEPTED_INSURANCES)
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    mock_orchestrator_service.validate_insurance.assert_called_once_with(insurance_name)
    
    # Check the rejection message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert f"não estamos atendendo o convênio '{insurance_name}'" in call_args[1]
    assert f"Aceitamos: {accepted_insurances_str}" in call_args[1]
    assert "Gostaria de seguir como particular ou tentar informar outro convênio?" in call_args[1]
    
    # Check the state transition back to AWAITING_TYPE
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "AWAITING_TYPE", 
        initial_context # Context might be reset or kept, check implementation (currently kept)
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_docs_insurance(
    mock_state_service,
    mock_whatsapp_service,
    mock_background_tasks
):
    """ Test receiving a message (assumed docs) in AWAITING_DOCS_INSURANCE state. """
    phone_number = "1234567897"
    message_text = "aqui estão os documentos" # Actual content doesn't matter for this test
    initial_context = {"is_private": False, "insurance_name": "GoodHealth"}
    payload = create_whatsapp_payload(phone_number, message_text)
    
    # Set initial state
    mock_state_service.get_state.return_value = {"state": "AWAITING_DOCS_INSURANCE", "context": initial_context}
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    
    # Check the slot preference prompt was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Obrigado! Agora, sobre o agendamento" in call_args[1]
    assert "preferência de dia ou horário" in call_args[1]
    
    # Check the state transition
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "AWAITING_SLOT_PREFERENCE", 
        initial_context # Context should be preserved
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_slot_preference_slots_available(
    mock_state_service,
    mock_whatsapp_service,
    mock_scheduling_service, # Need scheduling service
    mock_background_tasks
):
    """ Test asking for slots in AWAITING_SLOT_PREFERENCE with available slots. """
    phone_number = "1234567898"
    message_text = "qualquer horário serve"
    initial_context = {"is_private": False, "insurance_name": "GoodHealth"}
    payload = create_whatsapp_payload(phone_number, message_text)
    
    # Define available slots
    available_slots = [
        {"slot_id": "slot1", "start_time": "2024-08-01T10:00:00", "end_time": "2024-08-01T10:30:00"},
        {"slot_id": "slot2", "start_time": "2024-08-01T11:00:00", "end_time": "2024-08-01T11:30:00"}
    ]
    
    # Set initial state and mock service results
    mock_state_service.get_state.return_value = {"state": "AWAITING_SLOT_PREFERENCE", "context": initial_context}
    mock_scheduling_service.get_available_slots.return_value = available_slots
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    mock_scheduling_service.get_available_slots.assert_called_once()
    
    # Check the slot list message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Aqui estão os próximos horários disponíveis:" in call_args[1]
    assert "01/08/2024 às 10:00 (ID: slot1)" in call_args[1] # Check formatting
    assert "01/08/2024 às 11:00 (ID: slot2)" in call_args[1]
    assert "digite o ID do horário que deseja escolher" in call_args[1]
    
    # Check the state transition
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "AWAITING_SLOT_CHOICE", 
        initial_context # Context should be preserved
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_slot_preference_no_slots(
    mock_state_service,
    mock_whatsapp_service,
    mock_scheduling_service, # Need scheduling service
    mock_background_tasks
):
    """ Test asking for slots in AWAITING_SLOT_PREFERENCE with no available slots. """
    phone_number = "1234567899"
    message_text = "tem horário hoje?"
    initial_context = {"is_private": False, "insurance_name": "GoodHealth"}
    payload = create_whatsapp_payload(phone_number, message_text)
    
    # Set initial state and mock service results
    mock_state_service.get_state.return_value = {"state": "AWAITING_SLOT_PREFERENCE", "context": initial_context}
    mock_scheduling_service.get_available_slots.return_value = [] # No slots
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    mock_scheduling_service.get_available_slots.assert_called_once()
    
    # Check the no slots message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Desculpe, no momento não há horários disponíveis" in call_args[1]
    
    # Check the state remains the same
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "AWAITING_SLOT_PREFERENCE", # Stays in the same state
        initial_context 
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_slot_choice_success(
    mock_state_service,
    mock_whatsapp_service,
    mock_scheduling_service, # Need scheduling service
    mock_background_tasks
):
    """ Test successfully reserving a slot in AWAITING_SLOT_CHOICE state. """
    phone_number = "1234567900"
    chosen_slot_id = "slot1"
    initial_context = {"is_private": False, "insurance_name": "GoodHealth"}
    payload = create_whatsapp_payload(phone_number, chosen_slot_id)
    
    # Mock successful reservation
    # Assuming reserve_slot returns formatted time on success
    reservation_result = {"success": True, "formatted_time": "01/08/2024 às 10:00"}
    
    # Set initial state and mock service results
    mock_state_service.get_state.return_value = {"state": "AWAITING_SLOT_CHOICE", "context": initial_context}
    mock_scheduling_service.reserve_slot.return_value = reservation_result
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    mock_scheduling_service.reserve_slot.assert_called_once_with(chosen_slot_id)
    
    # Check the confirmation message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Ótimo! Seu horário para 01/08/2024 às 10:00 foi pré-agendado" in call_args[1]
    assert "Nossa equipe irá verificar os documentos" in call_args[1]
    
    # Check the state transition to APPOINTMENT_PENDING
    expected_context = initial_context.copy()
    expected_context["reserved_slot_id"] = chosen_slot_id
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "APPOINTMENT_PENDING", 
        expected_context 
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_slot_choice_fail_retry(
    mock_state_service,
    mock_whatsapp_service,
    mock_scheduling_service, # Need scheduling service
    mock_background_tasks
):
    """ Test failing to reserve a slot (e.g., taken) but other slots are available. """
    phone_number = "1234567901"
    chosen_slot_id = "slot_taken"
    initial_context = {"is_private": False, "insurance_name": "GoodHealth"}
    payload = create_whatsapp_payload(phone_number, chosen_slot_id)
    
    # Mock failed reservation
    reservation_result = {"success": False, "error": "Slot just became unavailable."}
    
    # Mock other available slots for retry
    available_slots_retry = [
        {"slot_id": "slot_other", "start_time": "2024-08-02T14:00:00", "end_time": "2024-08-02T14:30:00"}
    ]
    
    # Set initial state and mock service results
    mock_state_service.get_state.return_value = {"state": "AWAITING_SLOT_CHOICE", "context": initial_context}
    mock_scheduling_service.reserve_slot.return_value = reservation_result
    mock_scheduling_service.get_available_slots.return_value = available_slots_retry # Called after failure
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    mock_scheduling_service.reserve_slot.assert_called_once_with(chosen_slot_id)
    mock_scheduling_service.get_available_slots.assert_called_once() # Should be called to get new list
    
    # Check the error message AND the new slot list was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    assert "Slot just became unavailable." in call_args[1] # Error message
    assert "Por favor, escolha outro horário" in call_args[1]
    assert "Aqui estão os horários atualizados:" in call_args[1]
    assert "02/08/2024 às 14:00 (ID: slot_other)" in call_args[1] # New slot
    
    # Check the state remains AWAITING_SLOT_CHOICE for retry
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "AWAITING_SLOT_CHOICE", # Stay in the same state
        initial_context 
    )

@pytest.mark.asyncio
async def test_post_webhook_awaiting_slot_choice_fail_no_slots(
    mock_state_service,
    mock_whatsapp_service,
    mock_scheduling_service, # Need scheduling service
    mock_background_tasks
):
    """ Test failing to reserve a slot and no other slots are available. """
    phone_number = "1234567902"
    chosen_slot_id = "slot_last_one_taken"
    initial_context = {"is_private": False, "insurance_name": "GoodHealth"}
    payload = create_whatsapp_payload(phone_number, chosen_slot_id)
    
    # Mock failed reservation
    reservation_result = {"success": False, "error": "Slot invalid or taken."}
    
    # Mock no other available slots
    available_slots_retry = []
    
    # Set initial state and mock service results
    mock_state_service.get_state.return_value = {"state": "AWAITING_SLOT_CHOICE", "context": initial_context}
    mock_scheduling_service.reserve_slot.return_value = reservation_result
    mock_scheduling_service.get_available_slots.return_value = available_slots_retry # Called after failure
    
    response = client.post("/whatsapp_test/webhook", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    mock_state_service.get_state.assert_called_once_with(phone_number)
    mock_scheduling_service.reserve_slot.assert_called_once_with(chosen_slot_id)
    mock_scheduling_service.get_available_slots.assert_called_once() # Should be called
    
    # Check the final error message was sent
    mock_whatsapp_service.send_message.assert_called_once()
    call_args = mock_whatsapp_service.send_message.call_args[0]
    assert call_args[0] == phone_number
    # The initial error message might be combined or just the final one sent
    # Checking for the specific message when no slots are left after failure:
    assert "Desculpe, não há mais horários disponíveis no momento." in call_args[1]
    assert "Por favor, entre em contato conosco." in call_args[1]
    
    # Check the state transition to HUMAN_TAKEOVER
    mock_state_service.save_state.assert_called_once_with(
        phone_number, 
        "HUMAN_TAKEOVER", # Escalate to human
        initial_context 
    )

# TODO: Add tests for other states (AWAITING_INITIAL_CHOICE, AWAITING_TYPE, etc.)

# TODO: Add more tests for POST scenarios... 