import os
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Escopo necessário para usar a API do Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Caminho para o arquivo de credenciais baixado do Google Cloud (formato JSON)
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# ID do calendário onde os eventos serão criados (você pode encontrar no Google Calendar → Configurações → ID do calendário)
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

def get_available_slots(date: str) -> list[datetime]:
    """
    Retorna uma lista de horários disponíveis para um determinado dia.
    """
    service = get_calendar_service()

    # Define intervalo de busca para o dia
    start_of_day = datetime.fromisoformat(date).isoformat() + "Z"
    end_of_day = (datetime.fromisoformat(date) + timedelta(days=1)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    
    # Exemplo: gera horários entre 9h e 18h a cada 1 hora
    all_slots = [
        datetime.fromisoformat(date + f"T{hour:02d}:00:00")
        for hour in range(9, 18)
    ]

    booked_slots = [
        datetime.fromisoformat(event['start']['dateTime'])
        for event in events
    ]

    available_slots = [slot for slot in all_slots if slot not in booked_slots]
    return available_slots

def create_calendar_event(name: str, phone: str, slot: datetime) -> str:
    """
    Cria um evento no Google Calendar e retorna o link do evento criado.
    """
    service = get_calendar_service()

    event = {
        'summary': f'Consulta com {name}',
        'description': f'Telefone: {phone}',
        'start': {'dateTime': slot.isoformat(), 'timeZone': 'America/Sao_Paulo'},
        'end': {'dateTime': (slot + timedelta(minutes=30)).isoformat(), 'timeZone': 'America/Sao_Paulo'},
    }

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    return created_event.get('htmlLink')