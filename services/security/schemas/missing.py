import json
from datetime import date
from typing import Dict, Any
from pydantic import BaseModel
from services.security.models.status_missing import StatusMissingEnum

class MissingUpdate(BaseModel):
    id: int = None
    user_id: int = None
    name: str = None
    last_name: str = None
    age: int = None
    gender: str = None
    description: str = None
    birthdate: date = None
    disappearance_date: date = None
    place_of_disappearance: str = None
    status: StatusMissingEnum = None
    photo: str = None
    characteristics: str = None
    reporter_name: str = None
    reporter_phone: int = None
    event_photo: str = None
    location: Dict[str, Any] = None

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
    location: Any

    class Config:
        from_attributes = True
