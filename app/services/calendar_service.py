import os
import datetime
import logging
from dataclasses import dataclass
from typing import Optional, List
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from datetime import datetime, timedelta, time
from app.services.scheduling_preferences import (
    SchedulingOptimizer,
    PatientPreferences
)
from app.config.clinic_settings import ClinicSettings
import json
import pytz

# Configurar logging
logger = logging.getLogger(__name__)

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

@dataclass
class CalendarEvent:
    """Estrutura para representar um evento no calendário"""
    start_time: datetime
    end_time: datetime
    patient_name: str
    patient_phone: str
    reason: str
    insurance: Optional[str] = None

# Define the SCOPES. If modifying these scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Define paths relative to the app directory
# Assumes the script is run from the project root
SECRETS_DIR = os.path.join('app', 'secrets')
CREDENTIALS_PATH = os.path.join(SECRETS_DIR, 'credentials.json')
SERVICE_ACCOUNT_PATH = os.path.join(SECRETS_DIR, 'service_account.json')
TOKEN_PATH = os.path.join(SECRETS_DIR, 'token.json')

class CalendarService:
    """Serviço para integração com o Google Calendar"""
    
    def __init__(self):
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        self.credentials = self._get_credentials()
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.optimizer = SchedulingOptimizer()
    
    def _get_credentials(self) -> Credentials:
        """
        Obtém as credenciais do Google Calendar.
        
        Tenta primeiro usar Service Account, e caso não encontre,
        usa autenticação OAuth.
        
        Returns:
            Credentials: Credenciais para a API do Google Calendar
        """
        try:
            # Verifica se existe um arquivo de conta de serviço e tenta usá-lo primeiro
            if os.path.exists(SERVICE_ACCOUNT_PATH):
                logger.info("Usando credenciais de conta de serviço")
                return service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_PATH, scopes=SCOPES
                )
            
            # Caso não exista conta de serviço, tenta autenticação OAuth
            creds = None
            # Se existe um arquivo de token, carrega as credenciais dele
            if os.path.exists(TOKEN_PATH):
                # Use Credentials.from_authorized_user_file for safer loading
                try:
                    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
                    logger.info("Loaded credentials from token.json")
                except Exception as e:
                    logger.warning(f"Could not load token file ({TOKEN_PATH}): {e}. Will attempt re-authentication.")
                    creds = None # Ensure creds is None if loading fails
            
            # Se não há credenciais válidas, ou elas expiraram, solicita novas
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    # Renova o token se expirado
                    logger.info("Refreshing expired credentials...")
                    creds.refresh(Request())
                else:
                    # Realiza novo fluxo de autenticação
                    logger.info("No valid credentials found, initiating OAuth flow...")
                    if not os.path.exists(CREDENTIALS_PATH):
                        raise FileNotFoundError(
                            f"Arquivo de credenciais não encontrado em {CREDENTIALS_PATH}. "
                            "Siga as instruções em app/secrets/README.md para configurar as credenciais."
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_PATH, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Salva as credenciais para uso futuro
                with open(TOKEN_PATH, 'w') as token:
                    # Use creds.to_json() for standard JSON serialization
                    token.write(creds.to_json())
                    logger.info(f"Saved credentials to {TOKEN_PATH}")
            
            return creds
        
        except Exception as e:
            logger.error(f"Erro ao obter credenciais do Google Calendar: {e}")
            # Retorna None para permitir mock em testes
            return None
    
    def check_availability(self, start_time: datetime, duration: int = ClinicSettings.DEFAULT_APPOINTMENT_DURATION) -> bool:
        """
        Verifica se um horário específico está disponível.
        
        Args:
            start_time: Horário de início da consulta
            duration: Duração da consulta em minutos
            
        Returns:
            bool: True se o horário estiver disponível, False caso contrário
        """
        try:
            # Verifica se o horário está dentro do horário de funcionamento
            if not self._is_within_working_hours(start_time, duration):
                logger.info(f"Horário {start_time} fora do horário de funcionamento")
                return False
            
            # Verifica se temos credenciais e serviço configurados
            if not self.credentials or not self.service:
                logger.error("Credenciais ou serviço não disponíveis")
                return False
                
            # Define the local timezone
            local_tz = pytz.timezone('America/Sao_Paulo') # Or your specific timezone
            
            # Ensure start_time is timezone-aware
            if start_time.tzinfo is None:
                aware_start_time = local_tz.localize(start_time)
            else:
                aware_start_time = start_time.astimezone(local_tz)
            
            # Calculate end time based on the aware start time
            aware_end_time = aware_start_time + timedelta(minutes=duration)
            
            logger.info(f"Verificando disponibilidade (aware): {aware_start_time} - {aware_end_time}")
            
            # Formata as datas para ISO8601 (timezone info is now included)
            time_min = aware_start_time.isoformat()
            time_max = aware_end_time.isoformat()
            
            # Tenta até 3 vezes em caso de erros temporários
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    events = self.service.events().list(
                        calendarId=self.calendar_id,
                        timeMin=time_min,
                        timeMax=time_max,
                        singleEvents=True
                    ).execute()
                    
                    is_available = len(events.get('items', [])) == 0
                    # Log using the original naive start_time for consistency if needed, or use aware_start_time
                    logger.info(f"Horário {start_time.strftime('%Y-%m-%d %H:%M')} ({local_tz.zone}) {'disponível' if is_available else 'indisponível'}")
                    return is_available
                except HttpError as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logger.error(f"Erro ao verificar disponibilidade após {max_retries} tentativas: {e}")
                        return False
                    logger.warning(f"Tentativa {retry_count}/{max_retries} falhou: {e}")
                    # Aguarda um pouco antes de tentar novamente
                    import time
                    time.sleep(1)
        
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade: {e}")
            return False
    
    def get_available_slots(self, 
                          date: datetime,
                          duration: int = ClinicSettings.DEFAULT_APPOINTMENT_DURATION,
                          preferences: Optional[PatientPreferences] = None) -> List[datetime]:
        """
        Retorna uma lista de horários disponíveis para um dia específico.
        
        Args:
            date: Data para verificar disponibilidade
            duration: Duração da consulta em minutos
            preferences: Preferências do paciente para otimização
            
        Returns:
            List[datetime]: Lista de horários disponíveis
        """
        # Map weekday() result (Mon=0, Sun=6) to ClinicSettings keys
        day_mapping = {
            0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'friday',
            5: 'saturday',
            6: 'sunday' # Add sunday even if not typically used, for completeness
        }
        
        try:
            # Get numeric weekday and map to English name
            weekday_num = date.weekday()
            day_key = day_mapping.get(weekday_num)

            # Verifica se é um dia de funcionamento using the English key
            # day = date.strftime('%A').lower() # OLD WAY
            if not day_key or day_key not in ClinicSettings.WORKING_DAYS:
                # Log the original Portuguese name for clarity if possible
                try:
                    locale_day_name = date.strftime('%A')
                except:
                    locale_day_name = f"Weekday {weekday_num}" # Fallback
                logger.info(f"Dia {date.strftime('%d/%m/%Y')} ({locale_day_name}) não é dia de funcionamento (key: {day_key})")
                return []
            
            logger.info(f"Buscando slots disponíveis para {date.strftime('%d/%m/%Y')} (key: {day_key})")
            
            # Obtém os slots disponíveis para o dia using the English key
            available_slots = []
            # Use day_key for the lookup in ClinicSettings
            for slot_time in ClinicSettings.get_available_slots(day_key):
                slot = datetime.combine(date.date(), slot_time)
                if self.check_availability(slot, duration):
                    available_slots.append(slot)
            
            logger.info(f"Encontrados {len(available_slots)} slots disponíveis")
            
            # Se houver preferências, otimiza os slots
            if preferences:
                logger.info("Otimizando slots com base nas preferências do paciente")
                available_slots = self.optimizer.get_optimal_slots(
                    available_slots,
                    preferences,
                    duration
                )
            
            return available_slots
        
        except Exception as e:
            logger.error(f"Erro ao buscar slots disponíveis: {e}")
            return []
    
    def _is_within_working_hours(self, start_time: datetime, duration: int) -> bool:
        """Verifica se o horário está dentro do horário de funcionamento"""
        # Map weekday() result (Mon=0, Sun=6) to ClinicSettings keys
        day_mapping = {
            0: 'monday',
            1: 'tuesday',
            2: 'wednesday',
            3: 'thursday',
            4: 'friday',
            5: 'saturday',
            6: 'sunday'
        }
        
        # Get numeric weekday and map to English name
        weekday_num = start_time.weekday()
        day_key = day_mapping.get(weekday_num)
        
        # day = start_time.strftime('%A').lower() # OLD WAY
        if not day_key or day_key not in ClinicSettings.WORKING_HOURS:
            return False
        
        hours = ClinicSettings.WORKING_HOURS[day_key] # Use the mapped key
        slot_time = start_time.time()
        slot_end = (start_time + timedelta(minutes=duration)).time()
        
        return (hours['start'] <= slot_time and 
                slot_end <= hours['end'])
    
    def _is_lunch_time(self, start_time: datetime, duration: int) -> bool:
        """Verifica se o horário está dentro do período de almoço"""
        slot_time = start_time.time()
        slot_end = (start_time + timedelta(minutes=duration)).time()
        
        return (ClinicSettings.LUNCH_TIME_START <= slot_time < ClinicSettings.LUNCH_TIME_END or
                ClinicSettings.LUNCH_TIME_START < slot_end <= ClinicSettings.LUNCH_TIME_END)
    
    def create_calendar_event(self, event: CalendarEvent) -> str:
        """
        Cria um evento no calendário.
        
        Args:
            event: Dados do evento a ser criado
            
        Returns:
            str: ID do evento criado
        """
        calendar_event = {
            'summary': f'Consulta: {event.patient_name}',
            'description': f'Paciente: {event.patient_name}\n'
                         f'Telefone: {event.patient_phone}\n'
                         f'Motivo: {event.reason}\n'
                         f'Convênio: {event.insurance or "Particular"}',
            'start': {
                'dateTime': event.start_time.isoformat(),
                'timeZone': 'America/Sao_Paulo'
            },
            'end': {
                'dateTime': event.end_time.isoformat(),
                'timeZone': 'America/Sao_Paulo'
            }
        }
        
        created_event = self.service.events().insert(
            calendarId=self.calendar_id,
            body=calendar_event
        ).execute()
        
        return created_event['id']
    
    def cancel_appointment(self, event_id: str) -> bool:
        """
        Cancela um agendamento.
        
        Args:
            event_id: ID do evento a ser cancelado
            
        Returns:
            bool: True se o cancelamento foi bem sucedido, False caso contrário
        """
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()
            return True
        except Exception:
            return False

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