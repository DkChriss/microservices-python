from pydantic import BaseModel, EmailStr
from typing import Optional, List
from services.security.models.status_enum import StatusEnum

class UserStore(BaseModel):
    code: str
    name: str
    last_name: str
    second_surname: str
    email: EmailStr
    avatar: str
    status: StatusEnum
    password: str
    phone: int
    token_firebase: str = None
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    id: Optional[int] = None
    code: str | None
    name: str | None
    last_name:  str | None
    second_surname: str | None
    email: EmailStr | None
    avatar: str | None
    status: StatusEnum | None
    password: Optional[str] = None
    phone: int | None
    token_firebase: str | None
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    code: str
    name: str
    last_name: str
    second_surname: str
    email: EmailStr
    avatar: str
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