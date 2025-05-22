from pydantic import BaseModel


class EmergencyContactStore(BaseModel):
    user_id: int
    name: str
    line: str
    phone: int

class EmergencyContactUpdate(BaseModel):
    id: int = None
    user_id: int = None
    name: str = None
    line: str = None
    phone: int = None

class EmergencyContactResponse(BaseModel):
    id: int
    name: str
    line: str
    phone: int

    class Config:
        from_attributes = True