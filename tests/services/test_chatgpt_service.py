import pytest
from unittest.mock import patch, MagicMock
from app.services.chatgpt_service import ChatGPTService
import os

@pytest.fixture
def mock_openai_response():
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(
                content="Default mock response"
            )
        )
    ]
    return mock_response

@pytest.fixture
def chatgpt_service_with_mock():
    """Fixture to provide ChatGPTService with mocked API call."""
    # Patch the API key environment variable for initialization
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}), \
         patch('app.services.chatgpt_service.OpenAI') as MockOpenAI: # Mock the class itself
        
        # Configure the mock instance returned by OpenAI()
        mock_client_instance = MagicMock()
        MockOpenAI.return_value = mock_client_instance
        
        # Mock the specific method call
        mock_create_method = MagicMock()
        mock_client_instance.chat.completions.create = mock_create_method
        
        # Initialize the service - it will now use the mocked client instance
        service = ChatGPTService()
        
        # Yield the service and the specific mock method for tests
        yield service, mock_create_method 

def test_generate_response(chatgpt_service_with_mock, mock_openai_response):
    # Arrange
    service, mock_create = chatgpt_service_with_mock
    prompt = "Hello"
    system_message = "You are a test assistant"
    mock_create.return_value = mock_openai_response

    # Act
    response = service.generate_response(prompt, system_message)

    # Assert
    assert response == "Default mock response"
    mock_create.assert_called_once()
    call_args = mock_create.call_args[1]
    
    assert call_args['messages'] == [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

def test_analyze_patient_type_insurance(chatgpt_service_with_mock, mock_openai_response):
    # Arrange
    service, mock_create = chatgpt_service_with_mock
    message = "I want to schedule with my Unimed insurance"
    json_response = '''

    {
        "type": "insurance",
        "insurance_name": "Unimed",
        "confidence": 0.95
    }'''
    mock_openai_response.choices[0].message.content = json_response 
    mock_create.return_value = mock_openai_response

    # Act
    result = service.analyze_patient_type(message)

    # Assert
    assert result["type"] == "insurance"
    assert result["insurance_name"] == "Unimed"
    assert result["confidence"] == 0.95
    mock_create.assert_called_once()

def test_analyze_patient_type_private(chatgpt_service_with_mock, mock_openai_response):
    # Arrange
    service, mock_create = chatgpt_service_with_mock
    message = "I want to schedule a private appointment"
    json_response = '''
    {
        "type": "private",
        "insurance_name": null,
        "confidence": 0.9
    }'''
    mock_openai_response.choices[0].message.content = json_response 
    mock_create.return_value = mock_openai_response

    # Act
    result = service.analyze_patient_type(message)

    # Assert
    assert result["type"] == "private"
    assert result["insurance_name"] is None
    assert result["confidence"] == 0.9
    mock_create.assert_called_once()

def test_validate_insurance_accepted():
    # Arrange
    # This test doesn't involve API calls, so no need for the fixture
    # Patch env var for instantiation if necessary
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}): 
        service = ChatGPTService() 
        # Assuming ACCEPTED_INSURANCE_PROVIDERS is imported at the top of chatgpt_service.py
        # Use a known accepted value (replace if needed based on actual config)
        accepted_insurance = "Unimed" # Example

        # Act
        result = service.validate_insurance(accepted_insurance)

    # Assert
    assert result is True

def test_validate_insurance_not_accepted():
    # Arrange
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        service = ChatGPTService() 
        insurance_name = "Invalid Insurance"

        # Act
        result = service.validate_insurance(insurance_name)

    # Assert
    assert result is False

def test_generate_response_error(chatgpt_service_with_mock):
    # Arrange
    service, mock_create = chatgpt_service_with_mock
    mock_create.side_effect = Exception("API Error")

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        service.generate_response("test")
    assert "Failed to generate response from OpenAI" in str(exc_info.value)

def test_analyze_patient_type_invalid_json(chatgpt_service_with_mock, mock_openai_response):
    # Arrange
    service, mock_create = chatgpt_service_with_mock
    # Simulate model returning non-JSON content
    mock_openai_response.choices[0].message.content = "This is not JSON"
    mock_create.return_value = mock_openai_response

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        service.analyze_patient_type("test")
    # Expecting error from clean_json_response or json.loads within analyze_patient_type
    assert "Failed to analyze patient type" in str(exc_info.value)
    assert ("No valid JSON found" in str(exc_info.value) or 
            "json.decoder.JSONDecodeError" in str(exc_info.value)) # Check for either possible error 
