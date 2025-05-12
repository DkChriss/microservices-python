from pydantic import BaseModel, EmailStr


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class Token(BaseModel):
    access_token: str
    token_type: str