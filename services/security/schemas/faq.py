from pydantic import BaseModel


class FaqStore(BaseModel):
    question: str
    answer: str

class FaqUpdate(BaseModel):
    id: int = None
    question: str = None
    answer: str = None

class FaqResponse(BaseModel):
    id: int
    question: str
    answer: str

    class Config:
        from_attributes = True
