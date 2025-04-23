import os
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()  # <-- isso carrega o .env automaticamente

# Escopo necessário para usar a API do Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Caminho para o arquivo de credenciais baixado do Google Cloud (formato JSON)
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# ID do calendário onde os eventos serão criados (você pode encontrar no Google Calendar → Configurações → ID do calendário)
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

def get_calendar_service():
    """
    Autentica e retorna uma instância do serviço da API do Google Calendar.
    """
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=credentials)
    return service

from datetime import datetime

def validate_date(date: str):
    try:
        datetime.fromisoformat(date)
    except ValueError:
        raise ValueError("Data inválida fornecida.")

from datetime import datetime, timedelta

def get_available_slots(date: str) -> list[datetime]:
    try:
        validate_date(date)
        service = get_calendar_service()

        start_of_day = datetime.fromisoformat(date)
        end_of_day = start_of_day + timedelta(days=1)

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_of_day.isoformat() + "Z",
            timeMax=end_of_day.isoformat() + "Z",
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        all_slots = [
            datetime.fromisoformat(date + f"T{hour:02d}:00:00")
            for hour in range(9, 18)
        ]

        def slot_is_free(slot):
            slot_end = slot + timedelta(hours=1)
            for event in events:
                # Remove timezone info (convert to naive)
                event_start = datetime.fromisoformat(event['start']['dateTime']).replace(tzinfo=None)
                event_end = datetime.fromisoformat(event['end']['dateTime']).replace(tzinfo=None)
                if event_start < slot_end and event_end > slot:
                    return False
            return True

        available_slots = [slot for slot in all_slots if slot_is_free(slot)]
    except Exception as e:
        print("Erro ao buscar slots:", e)
        available_slots = []

    print("Slots disponíveis:", available_slots)
    return available_slots