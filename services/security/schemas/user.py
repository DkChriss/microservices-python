from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union

class UserStore(BaseModel):
    code: str
    name: str
    last_name: str
    second_surname: str
    email: EmailStr
    avatar: str
    status: bool
    password: str
    phone: int
    token_firebase: str = None
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    code: str | None
    name: str | None
    last_name:  str | None
    second_surname: str | None
    email: EmailStr | None
    avatar: str | None
    status: bool | None
    password: str | None
    phone: int | None
    token_firebase: str | None
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    message: str
    data: Union[UserStore, UserUpdate]