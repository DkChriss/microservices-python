from pydantic import BaseModel


class FaqStore(BaseModel):
    question: str
    answer: str
    user_id: int
    category_id: int

class FaqUpdate(BaseModel):
    id: int = None
    question: str = None
    answer: str = None
    user_id: int = None
    category_id: int = None

class FaqResponse(BaseModel):
    id: int
    question: str
    answer: str

    class Config:
        from_attributes = True
