from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from app.models.notification_log import NotificationLog

class NotificationLogService:
    """
    Serviço para gerenciar logs de notificações.
    """
    
    def __init__(self):
        self.logs: List[NotificationLog] = []
    
    def create_log(
        self,
        patient_name: str,
        appointment_date: datetime,
        message: str,
        sent_by: str,
        notes: Optional[str] = None
    ) -> NotificationLog:
        """
        Cria um novo log de notificação.
        
        Args:
            patient_name: Nome do paciente
            appointment_date: Data da consulta
            message: Mensagem enviada
            sent_by: Nome do usuário que enviou a notificação
            notes: Observações adicionais (opcional)
            
        Returns:
            NotificationLog: O log criado
        """
        log = NotificationLog(
            id=str(uuid4()),
            patient_name=patient_name,
            appointment_date=appointment_date,
            message=message,
            sent_at=datetime.now(),
            sent_by=sent_by,
            notes=notes
        )
        self.logs.append(log)
        return log
    
    def get_log(self, log_id: str) -> Optional[NotificationLog]:
        """
        Retorna um log pelo ID.
        
        Args:
            log_id: ID do log
            
        Returns:
            Optional[NotificationLog]: O log encontrado ou None
        """
        return next((log for log in self.logs if log.id == log_id), None)
    
    def get_patient_logs(
        self,
        patient_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[NotificationLog]:
        """
        Retorna os logs de notificações de um paciente dentro de um período.
        
        Args:
            patient_name: Nome do paciente
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)
            
        Returns:
            List[NotificationLog]: Lista de logs encontrados
        """
        logs = [
            log for log in self.logs
            if log.patient_name == patient_name
            and (start_date is None or log.appointment_date >= start_date)
            and (end_date is None or log.appointment_date <= end_date)
        ]
        return sorted(logs, key=lambda x: x.appointment_date, reverse=True)
    
    def update_log_status(
        self,
        log_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> bool:
        """
        Atualiza o status de um log.
        
        Args:
            log_id: ID do log
            status: Novo status (pending, sent, failed)
            notes: Observações adicionais (opcional)
            
        Returns:
            bool: True se o log foi atualizado com sucesso
        """
        log = self.get_log(log_id)
        if log:
            log.status = status
            if notes:
                log.notes = notes
            return True
        return False 