import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Define the SCOPES. If modifying these scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Define paths relative to the app directory
# Assumes the script is run from the project root
SECRETS_DIR = os.path.join('app', 'secrets')
CREDENTIALS_PATH = os.path.join(SECRETS_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(SECRETS_DIR, 'token.json')

class CalendarService:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        """Handles the OAuth 2.0 authentication flow for Google Calendar API."""
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(TOKEN_PATH):
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            except Exception as e:
                print(f"Error loading token file: {e}. Need to re-authenticate.")
                creds = None
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("Credentials expired, refreshing...")
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}. Need to re-authenticate.")
                    creds = None # Force re-authentication
            else:
                # Only run the flow if credentials file exists
                if not os.path.exists(CREDENTIALS_PATH):
                    raise FileNotFoundError(f"Credentials file not found at {CREDENTIALS_PATH}. Please obtain it from Google Cloud Console.")
                
                print(f"Credentials not found or invalid. Starting auth flow using {CREDENTIALS_PATH}...")
                try:
                    # Use InstalledAppFlow for initial authorization
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                    # The port 0 allows it to find an available port dynamically
                    # You might need to adjust launch_browser=False depending on environment
                    creds = flow.run_local_server(port=0, launch_browser=True)
                    print("Authentication successful!")
                except Exception as e:
                    print(f"Error during authentication flow: {e}")
                    raise RuntimeError("Failed to complete Google authentication flow.") from e
            
            # Save the credentials for the next run
            try:
                os.makedirs(SECRETS_DIR, exist_ok=True) # Ensure secrets directory exists
                with open(TOKEN_PATH, 'w') as token:
                    token.write(creds.to_json())
                print(f"Credentials saved to {TOKEN_PATH}")
            except Exception as e:
                 print(f"Error saving token file: {e}")
                 # Proceed without saving if saving fails, but warn user

        try:
            service = build('calendar', 'v3', credentials=creds)
            print("Google Calendar service built successfully.")
            return service
        except HttpError as error:
            print(f'An error occurred building the Calendar service: {error}')
            raise RuntimeError("Failed to build Google Calendar service.") from error
        except Exception as e:
             print(f'An unexpected error occurred building the Calendar service: {e}')
             raise RuntimeError("Failed to build Google Calendar service.") from e

    def create_calendar_event(
        self,
        start_time: datetime,
        end_time: datetime,
        patient_name: str,
        patient_phone: str,
        reason: str
    ) -> bool:
        """
        Creates an event on the user's primary Google Calendar.

        Args:
            start_time: Start time as datetime object
            end_time: End time as datetime object
            patient_name: Name of the patient
            patient_phone: Phone number of the patient
            reason: Reason for the appointment

        Returns:
            bool: True if the event was created successfully, False otherwise.
        """
        if not self.service:
             print("ERROR: Google Calendar service not initialized.")
             return False

        # Convert datetime objects to ISO format with timezone
        start_time_iso = start_time.isoformat()
        end_time_iso = end_time.isoformat()

        # Construct the event body
        event = {
            'summary': f'Consulta - {patient_name}',
            'description': (
                f'Paciente: {patient_name}\n'
                f'Telefone: {patient_phone}\n'
                f'Motivo: {reason}'
            ),
            'start': {
                'dateTime': start_time_iso,
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_time_iso,
                'timeZone': 'America/Sao_Paulo',
            },
            'reminders': {
                'useDefault': True,
            },
        }

        try:
            print(f"Creating event: {event.get('summary')} from {start_time_iso} to {end_time_iso}")
            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f'Event created: {created_event.get("htmlLink")}')
            return True
        except HttpError as error:
            print(f'An HTTP error occurred creating the event: {error}')
            return False
        except Exception as e:
             print(f'An unexpected error occurred creating the event: {e}')
             return False

    def get_available_slots(self, date: datetime) -> list[datetime]:
        """
        Retorna uma lista de horários disponíveis no calendário para uma data específica.
        
        Args:
            date: Data para verificar disponibilidade
            
        Returns:
            list[datetime]: Lista de horários disponíveis
        """
        try:
            # Define o início e o fim do dia
            start_of_day = datetime.combine(date.date(), datetime.min.time())
            end_of_day = start_of_day + timedelta(days=1)

            # Busca eventos no calendário dentro do intervalo de tempo especificado
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat() + "Z",
                timeMax=end_of_day.isoformat() + "Z",
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            # Obtém a lista de eventos
            events = events_result.get('items', [])

            # Gera todos os horários possíveis entre 9h e 18h
            all_slots = [
                datetime.combine(date.date(), datetime.min.time().replace(hour=hour, minute=0))
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
            return available_slots

        except Exception as e:
            print(f"Erro ao buscar slots disponíveis: {e}")
            return []

def get_calendar_service():
    """
    Autentica e retorna uma instância do serviço da API do Google Calendar.
    """
    # Cria credenciais a partir do arquivo de conta de serviço
    credentials = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
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
            calendarId='primary',
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
            calendarId='primary',
            body=event
        ).execute()
        
        print(f'Evento criado: {event.get("htmlLink")}')
        return event
        
    except Exception as e:
        print(f"Erro ao criar evento no calendário: {e}")
        raise