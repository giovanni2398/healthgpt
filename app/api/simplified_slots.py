from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
import json
import os

from app.services.simplified_slot_service import SimplifiedSlotService

# Inicialização lazy do serviço
_service = None

def get_service():
    global _service
    if _service is None:
        _service = SimplifiedSlotService()
    return _service

simplified_slots_router = APIRouter(
    prefix="/api/simplified-slots",
    tags=["simplified-slots"],
    responses={404: {"description": "Not found"}},
)

# Modelos de dados
class SlotResponse(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    is_available: bool

class AppointmentRequest(BaseModel):
    patient_name: str
    contact: str
    reason: str = Field(..., description="Motivo da consulta")

class AppointmentResponse(BaseModel):
    start_time: datetime
    end_time: datetime
    patient_name: str
    contact: str
    reason: str

class ScheduleConfig(BaseModel):
    slot_duration_minutes: int = Field(45, description="Duração de cada slot em minutos")
    schedules: List[Dict] = Field(..., description="Lista de configurações de horários")

class AppointmentInfo(BaseModel):
    """Information needed to book an appointment."""
    name: str = Field(..., description="Patient name")
    phone: str = Field(..., description="Contact phone number")
    reason: str = Field(..., description="Reason for appointment")
    email: Optional[str] = Field(None, description="Email address for confirmation (optional)")
    notes: Optional[str] = Field(None, description="Additional notes")

class Slot(BaseModel):
    """A time slot for an appointment."""
    id: str = Field(..., description="Unique ID for the slot")
    start_time: str = Field(..., description="ISO format start time")
    end_time: str = Field(..., description="ISO format end time")
    is_available: bool = Field(..., description="Whether the slot is available for booking")

class ApiResponse(BaseModel):
    """Generic API response model."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="A message describing the result")
    data: Optional[Dict] = Field(None, description="Response data if any")

# Dependency for SimplifiedSlotService
def get_slot_service():
    """Dependency to provide the slot service instance."""
    return SimplifiedSlotService()

@simplified_slots_router.get("/available", response_model=List[Slot])
async def get_available_slots(
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date in ISO format (YYYY-MM-DD)"),
    slot_service: SimplifiedSlotService = Depends(get_slot_service)
):
    """Get available slots between the given dates."""
    try:
        # Parse the start date
        start = datetime.fromisoformat(start_date)
        
        # If end date is not provided, default to 4 weeks ahead
        if not end_date:
            end = start + timedelta(weeks=4)
        else:
            end = datetime.fromisoformat(end_date)
        
        # Get available slots
        slots = slot_service.get_available_slots(start, end)
        
        # Format for response
        formatted_slots = []
        for slot in slots:
            formatted_slots.append({
                "id": slot["id"],
                "start_time": slot["start_time"].isoformat(),
                "end_time": slot["end_time"].isoformat(),
                "is_available": slot["is_available"]
            })
        
        return formatted_slots
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")

@simplified_slots_router.post("/book", response_model=ApiResponse)
async def book_slot(
    start_time: str = Query(..., description="Start time in ISO format"),
    appointment: AppointmentInfo,
    slot_service: SimplifiedSlotService = Depends(get_slot_service)
):
    """Book a slot for an appointment."""
    try:
        # Parse the start time
        start = datetime.fromisoformat(start_time)
        
        # Prepare appointment info
        appointment_dict = appointment.dict()
        
        # Book the slot
        success = slot_service.book_slot(start, appointment_dict)
        
        if success:
            return {
                "success": True,
                "message": "Appointment booked successfully",
                "data": {
                    "start_time": start_time,
                    "appointment": appointment_dict
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to book appointment. The slot may already be taken.",
                "data": None
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")

@simplified_slots_router.post("/cancel", response_model=ApiResponse)
async def cancel_appointment(
    start_time: str = Query(..., description="Start time in ISO format"),
    slot_service: SimplifiedSlotService = Depends(get_slot_service)
):
    """Cancel an appointment."""
    try:
        # Parse the start time
        start = datetime.fromisoformat(start_time)
        
        # Get the appointment before canceling (to include in response)
        appointment = slot_service.get_appointment(start)
        
        # Cancel the appointment
        success = slot_service.cancel_appointment(start)
        
        if success:
            return {
                "success": True,
                "message": "Appointment canceled successfully",
                "data": {
                    "start_time": start_time,
                    "appointment": appointment
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to cancel appointment. The appointment may not exist.",
                "data": None
            }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")

@simplified_slots_router.get("/appointments", response_model=List[AppointmentResponse])
async def get_all_appointments(
    slot_service: SimplifiedSlotService = Depends(get_slot_service)
):
    """Get all appointments."""
    # Get all appointments
    appointments = slot_service.get_all_appointments()
    
    # Format for response
    formatted_appointments = []
    for start_time, appointment in appointments.items():
        # Parse the start time to get end time
        start = datetime.fromisoformat(start_time)
        end = start + slot_service.slot_duration
        
        formatted_appointments.append({
            "start_time": start_time,
            "end_time": end.isoformat(),
            **appointment
        })
    
    return formatted_appointments

@simplified_slots_router.get("/appointment", response_model=Optional[AppointmentResponse])
async def get_appointment(
    start_time: str = Query(..., description="Start time in ISO format"),
    slot_service: SimplifiedSlotService = Depends(get_slot_service)
):
    """Get a specific appointment."""
    try:
        # Parse the start time
        start = datetime.fromisoformat(start_time)
        
        # Get the appointment
        appointment = slot_service.get_appointment(start)
        
        if not appointment:
            return None
        
        # Calculate end time
        end = start + slot_service.slot_duration
        
        # Format for response
        return {
            "start_time": start_time,
            "end_time": end.isoformat(),
            **appointment
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {str(e)}")

@simplified_slots_router.get("/config", response_model=ScheduleConfig)
async def get_schedule_config():
    """
    Retorna a configuração atual dos horários da clínica.
    """
    service = get_service()
    return service.config

@simplified_slots_router.put("/config", response_model=ScheduleConfig)
async def update_schedule_config(config: ScheduleConfig):
    """
    Atualiza a configuração dos horários da clínica.
    """
    service = get_service()
    
    # Validar a configuração
    if config.slot_duration_minutes <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A duração do slot deve ser um valor positivo"
        )
    
    if not config.schedules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deve haver pelo menos uma configuração de horário"
        )
    
    # Validar cada configuração de horário
    for schedule in config.schedules:
        if "days" not in schedule or not schedule["days"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cada configuração deve ter pelo menos um dia da semana"
            )
        
        if "start_time" not in schedule or "end_time" not in schedule:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cada configuração deve ter horário de início e fim"
            )
    
    # Salvar a nova configuração
    with open(service.schedule_config_file, 'w') as f:
        json.dump(config.dict(), f, indent=2)
    
    # Recarregar o serviço para aplicar as novas configurações
    global _service
    _service = None
    
    return config 