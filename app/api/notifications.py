from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.notification_log_service import NotificationLogService
from app.models.notification_log import NotificationLog

router = APIRouter()
notification_log_service = NotificationLogService()

class NotificationLogResponse(BaseModel):
    """Modelo de resposta para logs de notificações."""
    id: str
    patient_name: str
    appointment_date: datetime
    notification_type: str
    message: str
    sent_at: datetime
    sent_by: str
    status: str
    notes: Optional[str] = None

class UpdateNotificationStatusRequest(BaseModel):
    """Modelo de requisição para atualizar status de notificação."""
    status: str
    notes: Optional[str] = None

@router.get("/logs", response_model=List[NotificationLogResponse])
async def get_notification_logs(
    patient_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None
):
    """
    Retorna os logs de notificações com filtros opcionais.
    """
    try:
        if patient_name:
            logs = notification_log_service.get_patient_logs(
                patient_name=patient_name,
                start_date=start_date,
                end_date=end_date
            )
        else:
            # Se não houver filtro de paciente, retorna todos os logs
            logs = notification_log_service.logs
        
        # Aplica filtro de status se fornecido
        if status:
            logs = [log for log in logs if log.status == status]
        
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs/{log_id}", response_model=NotificationLogResponse)
async def get_notification_log(log_id: str):
    """
    Retorna um log específico pelo ID.
    """
    log = notification_log_service.get_log(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log não encontrado")
    return log

@router.put("/logs/{log_id}/status")
async def update_notification_status(
    log_id: str,
    request: UpdateNotificationStatusRequest
):
    """
    Atualiza o status de um log de notificação.
    """
    success = notification_log_service.update_log_status(
        log_id=log_id,
        status=request.status,
        notes=request.notes
    )
    if not success:
        raise HTTPException(status_code=404, detail="Log não encontrado")
    return {"message": "Status atualizado com sucesso"} 