from fastapi import APIRouter

router = APIRouter()

@router.get("/chatgpt/test")
async def test_chatgpt():
    return {"message": "ChatGPT route funcionando!"}
 
