from pydantic import BaseModel, EmailStr
from typing import Optional, List, Union

class UserStore(BaseModel):
    codigo: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    correo_electronico: EmailStr
    avatar: str
    estado: bool
    contraseña: str
    celular: int
    token_firebase: str = None
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    codigo: str | None
    nombre: str | None
    apellido_paterno:  str | None
    apellido_materno: str | None
    correo_electronico: EmailStr | None
    avatar: str | None
    estado: bool | None
    contraseña: str | None
    celular: int | None
    token_firebase: str | None
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    message: str
    data: Union[UserStore, UserUpdate]