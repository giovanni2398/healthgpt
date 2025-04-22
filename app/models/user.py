from pydantic import BaseModel

class User(BaseModel):
    name: str
    phone: str
    insurance: str | None = None
