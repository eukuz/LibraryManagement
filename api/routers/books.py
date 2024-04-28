from fastapi import APIRouter, Depends, Security, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, NonNegativeInt
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from api import di
from api.exceptions import NotFoundError
from api.persistence.models import Book, Collection
from api.services import books as books_service, collections
import asyncio


router = APIRouter()


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str

    read_pages: int
    total_pages: int

    in_collection: bool


class SearchBookResponse(BaseModel):
    books: list[BookResponse]


@router.get("/")
async def search_books(
    title_like: str = "",
    author_like: str = "",
    offset: int = 0,
    limit: int = 20,
    sessionmaker=Depends(di.sessionmaker),
    user_id=Depends(di.get_user_id),
) -> SearchBookResponse:
    books_ = await books_service.search_books(
        title_like,
        author_like,
        offset,
        limit,
        sessionmaker,
    )
    resp = SearchBookResponse(books=[])
    books = {
        book.id: BookResponse(
            id=book.id,
            title=book.title,
            author=book.author_id,
            genre=book.genre_name,
            read_pages=0,
            total_pages=book.pages,
            in_collection=False,
        )
        for book in books_
    }
    coros = {
        book.id: (
            asyncio.create_task(
                books_service.get_progress(book.id, user_id, sessionmaker)
            ),
            asyncio.create_task(
                collections.get_in_collection(book.id, user_id, sessionmaker)
            ),
        )
        for book in books_
    }
    for book_id, (progress_coro, in_coll_coro) in coros.items():
        progress = await progress_coro
        in_coll = await in_coll_coro
        books[book_id].read_pages = progress.read_pages
        books[book_id].in_collection = in_coll
    resp.books = list(books.values())
    return resp


@router.get("/suggest")
async def suggest_books(
    limit: int = 20,
    sessionmaker: async_sessionmaker[AsyncSession] = Depends(di.sessionmaker),
    user_id=Depends(di.get_user_id),
) -> SearchBookResponse:
    resp = SearchBookResponse(books=[])

    books = await books_service.suggest_books(user_id, limit, sessionmaker)

    resp.books = [
        BookResponse(
            id=book.id,
            title=book.title,
            author=book.author_id,
            genre=book.genre_name,
            read_pages=0,
            total_pages=book.pages,
            in_collection=False,
        )
        for book in books
    ]

    return resp


@router.get(
    "/{book_id}",
    responses={
        200: {
            "model": BookResponse,
        },
        404: {
            "description": "No such a book",
        },
    },
)
async def get_book(
    book_id: int,
    sessionmaker=Depends(di.sessionmaker),
    user_id=Security(di.get_user_id),
):
    book = await books_service.get_book(book_id, sessionmaker)
    if book is None:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)
    progress, in_collection = await asyncio.gather(
        books_service.get_progress(book_id, user_id, sessionmaker),
        collections.get_in_collection(book_id, user_id, sessionmaker),
    )
    return BookResponse(
        id=book.id,
        title=book.title,
        author=book.author.fullname,
        genre=book.genre_name,
        read_pages=progress.read_pages,
        total_pages=book.pages,
        in_collection=in_collection,
    )


@router.post("/{book_id}/collection")
async def set_in_collection(
    book_id: int,
    add: bool,
    user_id=Depends(di.get_user_id),
    sessionmaker=Depends(di.sessionmaker),
):
    try:
        await collections.set_in_collection(book_id, user_id, add, sessionmaker)
    except NotFoundError:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)


class SetProgressRequest(BaseModel):
    pages_read: NonNegativeInt


@router.post("/{book_id}/progress")
async def set_progress(
    __root__: SetProgressRequest,
    book_id: int,
    user_id=Security(di.get_user_id),
    sessionmaker=Depends(di.sessionmaker),
):
    req_body = __root__
    try:
        await books_service.set_progress(
            book_id, user_id, req_body.pages_read, sessionmaker
        )
    except NotFoundError:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)
