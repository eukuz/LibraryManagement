import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from api.persistence.models import Book, BookProgress
from api.exceptions import NotFoundError


logger = logging.getLogger(__name__)


async def search_books(
    title_like: str,
    author_like: str,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> list[Book]:
    async with sessionmaker() as session:
        stmt = select(Book)
        if title_like != "":
            stmt = stmt.where(Book.title.contains(title_like))
        if author_like != "":
            stmt = stmt.where(Book.author_id.contains(author_like))
        return list((await session.execute(stmt)).scalars())


async def get_book(
    _id: int,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> Book | None:
    async with sessionmaker() as session:
        stmt = select(Book).where(Book.id == _id)
        return (await session.execute(stmt)).scalar_one_or_none()


async def add_book(
    title: str,
    author_name: str,
    genre_name: str,
    pages: int,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> int:
    async with sessionmaker() as session:
        b = Book(
            title=title,
            author_id=author_name,
            genre_name=genre_name,
            pages=pages,
        )
        session.add(b)
        try:
            await session.commit()
        except IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise NotFoundError from e
            raise
        return b.id


async def get_progress(
    _id: int,
    user_id: str,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> BookProgress:
    async with sessionmaker() as session:
        stmt = select(BookProgress) \
            .where(BookProgress.book_id == _id) \
            .where(BookProgress.user_id == user_id)
        result = await session.execute(stmt)
        result = result.scalar_one_or_none()
        if result is None:
            result = BookProgress(book_id=_id, user_id=user_id, read_pages=0)
        return result


async def set_progress(
    _id: int,
    user_id: str,
    pages_read: int,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    async with sessionmaker() as session:
        progress = BookProgress(book_id=_id, user_id=user_id, read_pages=pages_read)
        session.add(progress)
        try:
            await session.commit()
        except IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise NotFoundError from e
            raise
