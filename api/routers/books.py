from fastapi import APIRouter, Depends, Security, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, NonNegativeInt
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from api import di
from api.exceptions import NotFoundError
from api.services import books as books_service, collections
from api.models.api import BookResponse, UNAUTHORIZED_ANSWER, NOT_FOUND_ANSWER


router = APIRouter()


class SearchBookResponse(BaseModel):
    books: list[BookResponse]


@router.get("/", responses={
    **UNAUTHORIZED_ANSWER,
})
async def search_books(
    title_like: str = "",
    author_like: str = "",
    offset: int = 0,
    limit: int = 20,
    sessionmaker=Depends(di.sessionmaker),
    user_id=Depends(di.get_user_id),
) -> SearchBookResponse:
    return SearchBookResponse(books=await books_service.search_books(
        user_id,
        title_like,
        author_like,
        offset,
        limit,
        sessionmaker,
    ))


@router.get("/suggest", responses={
    **UNAUTHORIZED_ANSWER,
})
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
        **UNAUTHORIZED_ANSWER,
        **NOT_FOUND_ANSWER,
    },
)
async def get_book(
    book_id: int,
    sessionmaker=Depends(di.sessionmaker),
    user_id=Security(di.get_user_id),
):
    book = await books_service.get_book(book_id, user_id, sessionmaker)
    if book is None:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)
    return book


@router.post("/{book_id}/collection", responses={
    **UNAUTHORIZED_ANSWER,
    **NOT_FOUND_ANSWER,
})
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


@router.post("/{book_id}/progress", responses={
    **UNAUTHORIZED_ANSWER,
    **NOT_FOUND_ANSWER,
})
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
        return JSONResponse({"description": "No such a book"}, status_code=status.HTTP_404_NOT_FOUND)
