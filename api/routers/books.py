from fastapi import APIRouter, Depends, Security, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, NonNegativeInt
from api import di
from api.exceptions import NotFoundError
from api.services import books, collections
import asyncio


router = APIRouter()


class BookResponse(BaseModel):
    title: str
    author: str
    genre: str

    read_pages: int
    total_pages: int

    in_collection: bool


@router.get(
    "/{book_id}",
    responses={
        200: {
            'model': BookResponse,
        },
        404: {
            'description': 'No such a book',
        }
    }
)
async def get_book(
    book_id: int,
    sessionmaker=Depends(di.sessionmaker),
    user_id=Security(di.get_user_id),
):
    book, progress, in_collection = await asyncio.gather(
        books.get_book(book_id, sessionmaker),
        books.get_progress(book_id, user_id, sessionmaker),
        collections.get_in_collection(book_id, user_id, sessionmaker),
    )
    if book is None:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)
    return BookResponse(
        title=book.title,
        author=book.author.fullname,
        genre=book.genre_name,
        read_pages=progress.read_pages,
        total_pages=book.pages,
        in_collection=in_collection
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
        await books.set_progress(book_id, user_id, req_body.pages_read, sessionmaker)
    except NotFoundError:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)
