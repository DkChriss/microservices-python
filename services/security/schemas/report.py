from pydantic import BaseModel
from sqlalchemy import DateTime


class ReportStore(BaseModel):
    missing_id: int
    user_id: int
    name: str
    email: str
    phone: str
    location: str
    date: DateTime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class ReportUpdate(BaseModel):
    id: int = None
    missing_id: int = None
    user_id: int = None
    name: str = None
    email: str = None
    phone: str = None
    location: str = None
    date: DateTime = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class ReportResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    location: str
    date: DateTime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True