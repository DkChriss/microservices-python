from pydantic import BaseModel


class CategoryStore(BaseModel):
    title: str
    slug: str

class CategoryUpdate(BaseModel):
    id: int = None
    title: str
    slug: str

class CategoryResponse(BaseModel):
    id: int
    title: str
    slug: str

    class Config:
        from_attributes = True