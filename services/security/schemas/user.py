from pydantic import BaseModel, EmailStr
from typing import List
from services.security.models.status_enum import StatusEnum

class UserResponse(BaseModel):
    id: int
    code: str
    name: str
    last_name: str
    second_surname: str
    email: EmailStr
    status: StatusEnum
    phone: int

    class Config:
        from_attributes = True

class UserRoles(BaseModel):
    user_id: int
    roles_ids: List[int]

class UserPermissions(BaseModel):
    user_id: int
    permissions_ids: List[int]