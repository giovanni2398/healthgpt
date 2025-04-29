from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from app.services.slot_management_service import SlotManagementService

router = APIRouter(prefix="/slots", tags=["slots"])

# Lazy-loaded service
_slot_management_service = None

def get_slot_service():
    global _slot_management_service
    if _slot_management_service is None:
        _slot_management_service = SlotManagementService(db_path="data/slots.db")
    return _slot_management_service


class SlotResponse(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    is_available: bool
    appointment_id: Optional[str] = None


class GenerateSlotsRequest(BaseModel):
    start_date: datetime = Field(..., description="Start date for slot generation")
    weeks_ahead: int = Field(4, description="Number of weeks to generate slots for")
    slot_duration_minutes: int = Field(30, description="Duration of each slot in minutes")
    daily_start_hour: int = Field(9, description="Start hour for each day (0-23)")
    daily_end_hour: int = Field(17, description="End hour for each day (0-23)")
    exclude_weekends: bool = Field(True, description="Whether to exclude weekends")


class BookSlotRequest(BaseModel):
    appointment_id: str = Field(..., description="ID of the appointment to book")


@router.post("/generate", response_model=Dict[str, int])
async def generate_slots(
    request: GenerateSlotsRequest,
    slot_service: SlotManagementService = Depends(get_slot_service)
):
    """Generate slots for the specified period."""
    try:
        excluded_days = [5, 6] if request.exclude_weekends else []
        
        num_slots = slot_service.generate_weekly_slots(
            start_date=request.start_date,
            weeks_ahead=request.weeks_ahead,
            slot_duration=timedelta(minutes=request.slot_duration_minutes),
            daily_start_time=timedelta(hours=request.daily_start_hour),
            daily_end_time=timedelta(hours=request.daily_end_hour),
            excluded_days=excluded_days
        )
        
        return {"slots_generated": num_slots}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/available", response_model=List[SlotResponse])
async def get_available_slots(
    start_date: datetime,
    end_date: datetime,
    slot_service: SlotManagementService = Depends(get_slot_service)
):
    """Get available slots in the specified date range."""
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    slots = slot_service.get_available_slots(start_date, end_date)
    return [SlotResponse(**slot) for slot in slots]


@router.post("/{slot_id}/book", response_model=Dict[str, bool])
async def book_slot(
    slot_id: str,
    request: BookSlotRequest,
    slot_service: SlotManagementService = Depends(get_slot_service)
):
    """Book a slot with the specified appointment ID."""
    success = slot_service.book_slot(slot_id, request.appointment_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Slot not found or already booked")
    
    return {"success": True}


@router.post("/cleanup", response_model=Dict[str, int])
async def cleanup_old_slots(
    slot_service: SlotManagementService = Depends(get_slot_service)
):
    """Remove slots that have already passed."""
    removed = slot_service.clear_old_slots()
    return {"slots_removed": removed} 