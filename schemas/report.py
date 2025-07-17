from pydantic import BaseModel
from datetime import datetime

class ReportStore(BaseModel):
    missing_id: int
    user_id: int
    name: str
    email: str
    phone: str
    location: str
    date: datetime
    description: str

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
    date: datetime = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class MissingInfo(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    location: str
    date: datetime
    description: str
    missing: MissingInfo

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True