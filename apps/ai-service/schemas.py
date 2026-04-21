from pydantic import BaseModel, ConfigDict, Field

class BlogPost(BaseModel):
    id: int
    title: str
    content: str

class AnalysisRequest(BaseModel):
    invoice: str | int

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
    is_offer: bool | None = None


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=50)


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: str