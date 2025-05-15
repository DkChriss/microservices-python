from pydantic import BaseModel

class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

class Token(BaseModel):
    token: str
    token_type: str
    user_id: int