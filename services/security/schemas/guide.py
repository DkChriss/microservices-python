from pydantic import BaseModel


class GuideStore(BaseModel):
    slug: str
    title: str
    subtitle: str
    content: str
    user_id: int
    category_id: int

class GuideUpdate(BaseModel):
    id: int = None
    slug: str = None
    title: str = None
    subtitle: str = None
    content: str = None
    user_id: int = None
    category_id: int = None


class GuideResponse(BaseModel):
    id: int
    slug: str
    title: str
    subtitle: str
    content: str

    class Config:
        from_attributes = True