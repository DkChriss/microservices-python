from pydantic import BaseModel


class EmergencyContactStore(BaseModel):
    user_id: int
    name: str
    line: str
    phone: str

class EmergencyContactUpdate(BaseModel):
    id: int = None
    user_id: int = None
    name: str = None
    line: str = None
    phone: str = None

class EmergencyContactResponse(BaseModel):
    id: int
    name: str
    line: str
    phone: str

    class Config:
        from_attributes = True