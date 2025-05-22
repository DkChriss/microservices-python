from typing import Dict, Any

from pydantic import BaseModel


class RequestStore(BaseModel):
    device_id: int
    address: str
    location: Dict[str, Any]
    wifi: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class RequestUpdate(BaseModel):
    id: int = None
    device_id: int = None
    address: str = None
    location: Dict[str, Any] = None
    wifi: str = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class RequestResponse(BaseModel):
    id: int
    address: str
    location: Dict[str, Any]
    wifi: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

