import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Force reload environment variables
load_dotenv(override=True)

from app.services.whatsapp_service import WhatsAppService

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Print environment variables (first few characters for security)
token = os.getenv("WHATSAPP_API_TOKEN")
phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
logger.info(f"Environment loaded - Token present: {'Yes' if token else 'No'}, Phone ID present: {'Yes' if phone_id else 'No'}")

# --- Parameters ---
# !!! IMPORTANT: Replace with a phone number you control for testing !!!
# Ensure the number is in E.164 format (e.g., +CountryCodeAreaCodeNumber)
RECIPIENT_PHONE_NUMBER = "+556199455691" 
TEST_PATIENT_NAME = "Paciente Teste" # Needed again for appointment_confirmation
TEST_APPOINTMENT_DATE = datetime(2024, 12, 25, 10, 30) # Needed again for appointment_confirmation

# --- Main Execution ---
try:
    logger.info("Initializing WhatsAppService...")
    whatsapp_service = WhatsAppService()

    # Check if credentials loaded (service constructor prints a warning if not)
    if not whatsapp_service.token or not whatsapp_service.phone_number_id:
        logger.error("WhatsApp credentials (Token or Phone Number ID) not found in .env. Exiting.")
        exit()

    # --- Code for sending 'hello_world' template (Commented out) ---
    # TEMPLATE_NAME = "hello_world"
    # LANGUAGE_CODE = "en_US" # Standard language for hello_world
    # logger.info(f"Attempting to send DIAGNOSTIC TEMPLATE '{TEMPLATE_NAME}' ({LANGUAGE_CODE}) to: {RECIPIENT_PHONE_NUMBER}")
    # # Use the generic send_template_message, no components needed for hello_world
    # success = whatsapp_service.send_template_message(
    #     phone=RECIPIENT_PHONE_NUMBER,
    #     template_name=TEMPLATE_NAME,
    #     language_code=LANGUAGE_CODE,
    #     components=None # Explicitly None
    # )

    # --- Code for sending appointment confirmation template (Re-enabled) ---
    TEMPLATE_NAME = "appointment_confirmation_v1" 
    
    logger.info(f"Attempting to send TEMPLATE '{TEMPLATE_NAME}' to: {RECIPIENT_PHONE_NUMBER}")
    logger.info(f"Patient Name: {TEST_PATIENT_NAME}, Appointment Date: {TEST_APPOINTMENT_DATE.strftime('%d/%m/%Y %H:%M')}")

    # Call the function and get the returned components list
    success, components_sent = whatsapp_service.send_appointment_confirmation(
        phone=RECIPIENT_PHONE_NUMBER,
        patient_name=TEST_PATIENT_NAME,
        appointment_date=TEST_APPOINTMENT_DATE,
        reason="Teste de Confirmação" # Reason is not used in the template but required by the function
    )

    # Print the components list *as received* from the function
    logger.info(f"Components list returned by send_appointment_confirmation: {components_sent}")

    if success:
        logger.info(f"Template message '{TEMPLATE_NAME}' sending reported as successful by the service (check WhatsApp!).")
    else:
        logger.error(f"Template message '{TEMPLATE_NAME}' sending failed according to the service. Check logs above for API errors.")

except Exception as e:
    logger.error(f"An unexpected error occurred during the script execution: {e}", exc_info=True)

logger.info("WhatsApp send test script finished.") 