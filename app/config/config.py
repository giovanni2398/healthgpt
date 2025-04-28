import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# Google Calendar Configuration
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# WhatsApp Configuration
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "your_verify_token")

# Application Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./health_gpt.db")

# Notification Configuration
NOTIFICATION_ENABLED = os.getenv("NOTIFICATION_ENABLED", "True").lower() == "true"
NOTIFICATION_INTERVAL = int(os.getenv("NOTIFICATION_INTERVAL", "60"))  # in minutes

# Clinic Configuration
CLINIC_NAME = os.getenv("CLINIC_NAME", "HealthGPT Nutrition Clinic")
CLINIC_ADDRESS = os.getenv("CLINIC_ADDRESS", "123 Health Street")
CLINIC_PHONE = os.getenv("CLINIC_PHONE", "+1234567890")
CLINIC_EMAIL = os.getenv("CLINIC_EMAIL", "contact@healthgpt.com")

# Business Hours
BUSINESS_HOURS = {
    "Monday": {"start": "09:00", "end": "17:00"},
    "Tuesday": {"start": "09:00", "end": "17:00"},
    "Wednesday": {"start": "09:00", "end": "17:00"},
    "Thursday": {"start": "09:00", "end": "17:00"},
    "Friday": {"start": "09:00", "end": "17:00"},
}

# Appointment Configuration
APPOINTMENT_DURATION = int(os.getenv("APPOINTMENT_DURATION", "60"))  # in minutes
MIN_SCHEDULE_NOTICE = int(os.getenv("MIN_SCHEDULE_NOTICE", "24"))  # in hours
MAX_SCHEDULE_ADVANCE = int(os.getenv("MAX_SCHEDULE_ADVANCE", "30"))  # in days

# Insurance Configuration
ACCEPTED_INSURANCE_PROVIDERS = [
    "Unimed",
    "Amil",
    "SulAmérica",
    "Bradesco Saúde",
    "NotreDame Intermédica"
] 