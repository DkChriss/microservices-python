from pydantic import BaseModel

class PermissionResponse(BaseModel):
    id: int
    name: str
    action: str
    model: str

    class Config:
        from_attributes = True