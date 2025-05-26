from pydantic import BaseModel
from typing import Any, Dict, Optional


class DeviceRegistrationStore(BaseModel):
    device_id: int
    location: Dict[str, Any]
    wifi: str

    class Config:
        arbitrary_types_allowed = True

class DeviceRegistrationUpdate(BaseModel):
    id: int = None
    device_id: int = None
    location: Dict[str, Any] = None
    wifi: str = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class DeviceRegistrationResponse(BaseModel):
    id: int
    location: Dict[str, Any]
    wifi: str

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True