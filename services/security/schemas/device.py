from pydantic import BaseModel


class DeviceStore(BaseModel):
    user_id: int
    code: str
    name: str
    password: str
    status: bool

class DeviceUpdate(BaseModel):
    id: int = None
    user_id: int = None
    code: str = None
    name: str = None
    password: str = None

class DeviceResponse(BaseModel):
    id: int
    user_id: int
    code: str
    name: str
    password: str

    class Config:
        from_attributes = True