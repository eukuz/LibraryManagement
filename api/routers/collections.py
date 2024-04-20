import asyncio
from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel
from api import di
from api.services import collections, books as books_service


router = APIRouter()


class CollectionItem(BaseModel):
    id: int
    title: str
    author: str
    genre: str

    read_pages: int
    total_pages: int


class CollectionResponse(BaseModel):
    books: list[CollectionItem]


@router.get("/")
async def get_collection(
    user_id=Security(di.get_user_id),
    sessionmaker=Depends(di.sessionmaker),
) -> CollectionResponse:
    books = await collections.get_collection(user_id, sessionmaker)
    progress = [
        asyncio.create_task(books_service.get_progress(book.id, user_id, sessionmaker))
        for book in books
    ]
    progress = await asyncio.gather(*progress)
    resp_books = []
    for pr in progress:
        resp_books.append(CollectionItem(
                id=pr.book.id,
                title=pr.book.title,
                author=pr.book.author_id,
                genre=pr.book.genre_name,
                read_pages=pr.read_pages,
                total_pages=pr.book.pages,
            )
        )
    return CollectionResponse(books=resp_books)
