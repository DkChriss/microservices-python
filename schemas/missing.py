from datetime import date
from pydantic import BaseModel
from models.status_missing import StatusMissingEnum

class MissingResponse(BaseModel):
    id: int
    name: str
    last_name: str
    age: int
    gender: str
    description: str
    birthdate: date
    disappearance_date: date
    place_of_disappearance: str
    status_missing: StatusMissingEnum
    characteristics: str
    reporter_name: str
    reporter_phone: int
    photo: str = None

    class Config:
        from_attributes = True
