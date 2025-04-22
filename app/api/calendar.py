from fastapi import APIRouter

router = APIRouter()

@router.get("/calendar/test")
async def test_calendar():
    return {"message": "Calendar route funcionando!"}
