import logging
import os
from dotenv import load_dotenv

from app.services.whatsapp_service import WhatsAppService

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env
load_dotenv()

# --- Parameters ---
RECIPIENT_PHONE_NUMBER = "+55(61)99945-5691" # Target number provided by user
TEST_MESSAGE = "Olá! Esta é uma mensagem de teste do HealthGPT."

# --- Main Execution ---
try:
    logger.info("Initializing WhatsAppService...")
    whatsapp_service = WhatsAppService()

    # Check if credentials loaded (service constructor prints a warning if not)
    if not whatsapp_service.token or not whatsapp_service.phone_number_id:
        logger.error("WhatsApp credentials (Token or Phone Number ID) not found in .env. Exiting.")
        exit()

    logger.info(f"Attempting to send test message to: {RECIPIENT_PHONE_NUMBER}")
    logger.info(f"Message content: {TEST_MESSAGE}")

    # --- Reverted to send a free-form text message ---
    success = whatsapp_service.send_message(
        phone=RECIPIENT_PHONE_NUMBER,
        message=TEST_MESSAGE
    )

    # --- Code for sending template message (commented out) ---
    # TEMPLATE_NAME = "hello_world"
    # LANGUAGE_CODE = "en_US"
    #
    # logger.info(f"Attempting to send TEMPLATE message: Name='{TEMPLATE_NAME}', Lang='{LANGUAGE_CODE}' to: {RECIPIENT_PHONE_NUMBER}")
    #
    # success = whatsapp_service.send_template_message(
    #     phone=RECIPIENT_PHONE_NUMBER,
    #     template_name=TEMPLATE_NAME,
    #     language_code=LANGUAGE_CODE
    # )

    if success:
        logger.info("Message sending reported as successful by the service (check WhatsApp!).")
    else:
        logger.error("Message sending failed according to the service. Check logs above for API errors.")

except Exception as e:
    logger.error(f"An unexpected error occurred during the script execution: {e}", exc_info=True)

logger.info("WhatsApp send test script finished.") 