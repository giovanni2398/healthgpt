from fastapi import APIRouter
from app.services.calendar_service import get_available_slots

router = APIRouter()

@router.get("/test")
async def test_calendar():
    return {"message": "Calendar route funcionando!"}

@router.get("/test-slots")
def test_slots():
    return get_available_slots("2025-04-23")
