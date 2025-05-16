from pydantic import BaseModel

from services.security.schemas.user import UserResponse


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class Token(BaseModel):
    token: str
    token_type: str
    user: UserResponse