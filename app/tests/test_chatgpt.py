import os
import pytest
from unittest.mock import patch, MagicMock
from app.services.chatgpt_service import ChatGPTService

def test_chatgpt_service_initialization():
    # Test successful initialization
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        service = ChatGPTService()
        assert service.api_key == "test_key"
        assert service.client is not None

    # Test initialization without API key
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            ChatGPTService()
        assert "OpenAI API key not found in environment variables" in str(exc_info.value)

@patch('app.services.chatgpt_service.OpenAI')
def test_generate_response_success(mock_openai):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Test response"
    mock_openai.return_value.chat.completions.create.return_value = mock_response

    # Test successful response generation
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        service = ChatGPTService()
        response = service.generate_response("Test prompt")
        
        assert response == "Test response"
        mock_openai.return_value.chat.completions.create.assert_called_once()

@patch('app.services.chatgpt_service.OpenAI')
def test_generate_response_error_handling(mock_openai):
    # Setup mock to raise an exception
    mock_openai.return_value.chat.completions.create.side_effect = Exception("Test error")

    # Test error handling
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        service = ChatGPTService()
        with pytest.raises(RuntimeError) as exc_info:
            service.generate_response("Test prompt")
        
        assert "Failed to generate response from OpenAI: Test error" in str(exc_info.value)

# Fixture for the real ChatGPT service
@pytest.fixture
def real_chatgpt_service(use_real_api):
    """Provides a real ChatGPTService instance, skipping if --use-real-api is not set."""
    if not use_real_api:
        pytest.skip("Skipping real API test for ChatGPT. Use --use-real-api flag to run.")
    
    print("\nInitializing real ChatGPTService...")
    try:
        service = ChatGPTService()
        # Quick check if API key seems loaded (though constructor already checks)
        if not service.api_key:
             pytest.fail("OpenAI API key seems missing even after initialization.")
        return service
    except ValueError as e:
        # Handle case where API key might still be missing despite user confirmation
        pytest.fail(f"ValueError during ChatGPTService initialization: {e}. Ensure OPENAI_API_KEY is correctly set in .env")
    except Exception as e:
        pytest.fail(f"Unexpected error initializing real ChatGPTService: {e}")

def test_real_generate_response(real_chatgpt_service):
    """Tests generate_response against the actual OpenAI API."""
    # The fixture real_chatgpt_service handles skipping and initialization
    service = real_chatgpt_service 
    
    print("Running test with REAL OpenAI API...")
    try:
        # Define a simple prompt
        prompt = "Translate the following English text to French: 'Hello, world!'"
        system_message = "You are a helpful translation assistant."
        
        print(f"Sending prompt to OpenAI: '{prompt}' with system message: '{system_message}'")
        
        # Call the real API
        response = service.generate_response(prompt, system_message)
        
        print(f"Received response from OpenAI: '{response}'")
        
        # Basic assertions: Check if response is a non-empty string
        assert isinstance(response, str)
        assert len(response) > 0
        assert "Bonjour" in response # Let's add a basic content check
        
        print("Real API test successful.")

    # No need for ValueError handling here, fixture handles initialization errors
    except RuntimeError as e:
        # Handle errors during API call (e.g., network issues, API errors)
        pytest.fail(f"RuntimeError during OpenAI API call: {e}")
    except Exception as e:
        # Catch any other unexpected errors
        pytest.fail(f"An unexpected error occurred during the real API test: {e}")
