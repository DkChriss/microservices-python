from pydantic import BaseModel, EmailStr


class ContactSupportStore(BaseModel):
    name: str
    email: EmailStr
    title: str
    message: str
    user_id: int

class ContactSupportUpdate(BaseModel):
    id: int = None
    name: str = None
    email: EmailStr = None
    title: str = None
    message: str = None
    user_id: int = None

class ContactSupportResponse(BaseModel):
    id: int = None
    name: str = None
    email: EmailStr = None
    title: str = None
    message: str = None

    class Config:
        from_attributes = True