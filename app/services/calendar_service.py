import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Escopo necessário para usar a API do Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Caminho para o arquivo de credenciais baixado do Google Cloud (formato JSON)
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

# ID do calendário onde os eventos serão criados
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

def get_calendar_service():
    """
    Autentica e retorna uma instância do serviço da API do Google Calendar.
    """
    # Cria credenciais a partir do arquivo de conta de serviço
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    # Constrói o serviço da API do Google Calendar
    service = build('calendar', 'v3', credentials=credentials)
    return service

def validate_date(date: str):
    """
    Valida se a data fornecida está no formato ISO 8601.
    """
    try:
        # Tenta converter a string para um objeto datetime
        datetime.fromisoformat(date)
    except ValueError:
        # Lança um erro se a data for inválida
        raise ValueError("Data inválida fornecida.")

def get_available_slots(date: str) -> list[datetime]:
    """
    Retorna uma lista de horários disponíveis no calendário para uma data específica.
    """
    try:
        # Valida a data fornecida
        validate_date(date)
        # Obtém o serviço do Google Calendar
        service = get_calendar_service()

        # Define o início e o fim do dia
        start_of_day = datetime.fromisoformat(date)
        end_of_day = start_of_day + timedelta(days=1)

        # Busca eventos no calendário dentro do intervalo de tempo especificado
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_of_day.isoformat() + "Z",  # Início do dia
            timeMax=end_of_day.isoformat() + "Z",    # Fim do dia
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        # Obtém a lista de eventos
        events = events_result.get('items', [])

        # Gera todos os horários possíveis entre 9h e 18h
        all_slots = [
            datetime.fromisoformat(date + f"T{hour:02d}:00:00")
            for hour in range(9, 18)
        ]

        def slot_is_free(slot):
            """
            Verifica se um horário está livre, considerando os eventos existentes.
            """
            # Define o fim do horário (1 hora de duração)
            slot_end = slot + timedelta(hours=1)
            for event in events:
                # Converte os horários dos eventos para objetos datetime sem timezone
                event_start = datetime.fromisoformat(event['start']['dateTime']).replace(tzinfo=None)
                event_end = datetime.fromisoformat(event['end']['dateTime']).replace(tzinfo=None)
                # Verifica se o horário do slot conflita com o evento
                if event_start < slot_end and event_end > slot:
                    return False
            return True

        # Filtra os horários disponíveis
        available_slots = [slot for slot in all_slots if slot_is_free(slot)]
    except Exception as e:
        # Trata erros e exibe uma mensagem
        print("Erro ao buscar slots:", e)
        available_slots = []

    # Exibe os horários disponíveis
    print("Slots disponíveis:", available_slots)
    return available_slots

def create_calendar_event(
    start_time: datetime,
    end_time: datetime,
    patient_name: str,
    patient_phone: str,
    reason: str
) -> dict:
    """
    Cria um evento no Google Calendar para um agendamento.
    
    Args:
        start_time: Data e hora de início do evento
        end_time: Data e hora de fim do evento
        patient_name: Nome do paciente
        patient_phone: Telefone do paciente
        reason: Motivo da consulta
    
    Returns:
        dict: Dados do evento criado
    """
    try:
        service = get_calendar_service()
        
        # Formata os horários para o formato ISO 8601 com timezone
        start_time_iso = start_time.isoformat() + "Z"
        end_time_iso = end_time.isoformat() + "Z"
        
        # Cria o evento
        event = {
            'summary': f'Consulta: {patient_name}',
            'description': f'Paciente: {patient_name}\nTelefone: {patient_phone}\nMotivo: {reason}',
            'start': {
                'dateTime': start_time_iso,
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_time_iso,
                'timeZone': 'America/Sao_Paulo',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                ],
            },
        }
        
        # Insere o evento no calendário
        event = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event
        ).execute()
        
        print(f'Evento criado: {event.get("htmlLink")}')
        return event
        
    except Exception as e:
        print(f"Erro ao criar evento no calendário: {e}")
        raise