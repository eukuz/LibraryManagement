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


class _Message(BaseModel):
    pass


UNAUTHORIZED_ANSWER = {401: {"model": _Message}}
NOT_FOUND_ANSWER = {404: {"model": _Message}}
