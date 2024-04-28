from pydantic import BaseModel


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str

    read_pages: int
    total_pages: int

    in_collection: bool


class CollectionItem(BaseModel):
    id: int
    title: str
    author: str
    genre: str

    read_pages: int
    total_pages: int
