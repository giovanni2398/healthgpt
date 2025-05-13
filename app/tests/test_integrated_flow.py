import pytest
import logging
from datetime import datetime, timedelta
from app.services.whatsapp_service import WhatsAppService
from app.services.chatgpt_service import ChatGPTService
from app.services.calendar_service import CalendarService
from app.services.conversation_state import ConversationManager
from app.config.clinic_settings import ClinicSettings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestIntegratedFlow:
    """Test suite for integrated system flow validation."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.whatsapp_service = WhatsAppService()
        self.chatgpt_service = ChatGPTService()
        self.calendar_service = CalendarService()
        self.conversation_manager = self.whatsapp_service.conversation_manager
        self.clinic_settings = ClinicSettings()
        
        # Test data
        self.test_patient = "Paciente Teste"
        self.test_phone = "+556199455691"
        self.test_date = datetime.now() + timedelta(days=1)
        self.test_time = "10:30"
        
    def test_private_appointment_flow(self):
        """Test complete flow for private appointment scheduling."""
        logger.info("Starting private appointment flow test")
        
        # 1. Initial message processing
        initial_message = "Olá, gostaria de marcar uma consulta particular"
        intent = self.chatgpt_service.analyze_patient_type(initial_message)
        assert intent["type"] == "private"
        logger.info("Initial message processed successfully")
        
        # 2. Check calendar availability
        available_slots = self.calendar_service.get_available_slots(self.test_date)
        assert len(available_slots) > 0
        logger.info(f"Found {len(available_slots)} available slots")
        
        # 3. Send appointment confirmation
        response = self.whatsapp_service.send_appointment_confirmation(
            self.test_phone,
            self.test_patient,
            self.test_date,
            reason="Consulta de Rotina"
        )
        assert response[0]  # First element of tuple indicates success
        logger.info("Appointment confirmation sent successfully")
        
        # 4. Verify conversation state
        state = self.conversation_manager.get_state(self.test_phone)
        assert state.value == "completed"
        logger.info("Conversation state verified")
        
    def test_insurance_appointment_flow(self):
        """Test complete flow for insurance appointment scheduling."""
        logger.info("Starting insurance appointment flow test")
        
        # 1. Initial message processing
        initial_message = "Olá, tenho Unimed e gostaria de marcar uma consulta"
        intent = self.chatgpt_service.analyze_patient_type(initial_message)
        assert intent["type"] == "insurance"
        assert intent["insurance_name"] == "Unimed"
        logger.info("Initial message processed successfully")
        
        # 2. Verify insurance
        insurance_valid = self.chatgpt_service.validate_insurance("Unimed")
        assert insurance_valid
        logger.info("Insurance validation successful")
        
        # 3. Check calendar availability
        available_slots = self.calendar_service.get_available_slots(self.test_date)
        assert len(available_slots) > 0
        logger.info(f"Found {len(available_slots)} available slots")
        
        # 4. Send appointment confirmation
        response = self.whatsapp_service.send_appointment_confirmation(
            self.test_phone,
            self.test_patient,
            self.test_date,
            reason="Consulta com Convênio"
        )
        assert response[0]  # First element of tuple indicates success
        logger.info("Appointment confirmation sent successfully")
        
        # 5. Verify conversation state
        state = self.conversation_manager.get_state(self.test_phone)
        assert state.value == "completed"
        logger.info("Conversation state verified")
        
    def test_error_handling(self):
        """Test system's error handling capabilities."""
        logger.info("Starting error handling test")
        
        # 1. Test invalid phone number
        invalid_phone = "123"
        response = self.whatsapp_service.send_appointment_confirmation(
            invalid_phone,
            self.test_patient,
            self.test_date,
            reason="Teste de Erro"
        )
        assert not response[0]  # First element of tuple indicates failure
        logger.info("Invalid phone number handled correctly")
        
        # 2. Test invalid date (using a date in the past)
        invalid_date = datetime.now() - timedelta(days=1)  # Yesterday
        available_slots = self.calendar_service.get_available_slots(invalid_date)
        assert len(available_slots) == 0
        logger.info("Invalid date handled correctly")
        
        # 3. Test invalid insurance
        insurance_valid = self.chatgpt_service.validate_insurance("InvalidInsurance")
        assert not insurance_valid
        logger.info("Invalid insurance handled correctly")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 