import logging
import random
from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from api.models.api import BookResponse
from api.persistence.models import Book, BookProgress, Collection, User
from api.services import collections
from api.exceptions import NotFoundError


logger = logging.getLogger(__name__)


async def search_books(
    user_id: str,
    title_like: str,
    author_like: str,
    offset: int,
    limit: int,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> list[BookResponse]:
    async with sessionmaker() as session:
        stmt = select(Book, BookProgress.read_pages, Collection.created_at) \
            .join(BookProgress, isouter=True) \
            .join(
                Collection,
                onclause=and_(
                    Collection.book_id == Book.id,
                    Collection.user_id == select(User.id).where(User.id == user_id).scalar_subquery(),
                ),
                isouter=True,
            )
        if title_like != "":
            stmt = stmt.where(Book.title.contains(title_like))
        if author_like != "":
            stmt = stmt.where(Book.author_id.contains(author_like))
        stmt = stmt.offset(offset).limit(limit)
        books = list(await session.execute(stmt))
        result: dict[str, BookResponse] = {}
        for (book, read_pages, created_at) in books:
            if book.id in result:
                if read_pages:
                    result[book.id].read_pages = read_pages
                continue
            result[book.id] = BookResponse(
                id=book.id,
                title=book.title,
                author=book.author_id,
                genre=book.genre_name,
                read_pages=read_pages or 0,
                total_pages=book.pages,
                in_collection=created_at is not None,
            )
        return list(result.values())


async def get_book(
    _id: int,
    user_id: str,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> BookResponse | None:
    async with sessionmaker() as session:
        stmt = select(Book, BookProgress.read_pages, Collection.created_at) \
            .where(Book.id == _id) \
            .join(BookProgress, isouter=True) \
            .join(
                Collection,
                onclause=and_(
                    Collection.book_id == Book.id,
                    Collection.user_id == select(User.id).where(User.id == user_id).scalar_subquery(),
                ),
                isouter=True,
            )
        book = list(await session.execute(stmt))
        if len(book) == 0:
            return None
        book, read_pages, created_at = book[0]
        return BookResponse(
            id=book.id,
            title=book.title,
            author=book.author_id,
            genre=book.genre_name,
            read_pages=read_pages or 0,
            total_pages=book.pages,
            in_collection=created_at is not None,
        )


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
        book = await get_book(_id, user_id, sessionmaker)
        if book is None:
            raise NotFoundError
    return result


async def set_progress(
    _id: int,
    user_id: str,
    pages_read: int,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    async with sessionmaker() as session:
        get_progress_stmt = select(BookProgress) \
            .where(BookProgress.book_id == _id) \
            .where(BookProgress.user_id == user_id)
        current_progress = (await session.execute(get_progress_stmt)).scalar_one_or_none()
        if current_progress is not None:
            await session.delete(current_progress)
        session.add(BookProgress(book_id=_id, user_id=user_id, read_pages=pages_read))
        try:
            await session.commit()
        except IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise NotFoundError from e
            raise


async def suggest_books(
    user_id: str,
    count: int,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> list[Book]:
    user_collection_stmt = select(Collection.book_id) \
        .where(Collection.user_id == user_id)
    user_collection = await collections.get_collection(user_id, sessionmaker)

    genre_count = {book.genre: 0 for book in user_collection}
    for book in user_collection:
        genre_count[book.genre] += 1

    top_genres = sorted(
        genre_count.items(),
        key=lambda x: x[1],
        reverse=True
    )
    top_genres = top_genres[:3]
    top_genres = [genre[0] for genre in top_genres]

    result: list[Book] = []

    same_genre_count = int(count * 0.75)
    async with sessionmaker() as session:
        stmt = select(Book) \
            .where(Book.id.not_in(user_collection_stmt)) \
            .where(Book.genre_name.in_(top_genres)) \
            .order_by(func.random()) \
            .limit(same_genre_count)
        result.extend((await session.execute(stmt)).scalars())

    max_size = count - len(result)
    async with sessionmaker() as session:
        stmt = select(Book) \
            .where(Book.id.not_in(user_collection_stmt)) \
            .where(Book.genre_name.not_in(genre_count.keys())) \
            .order_by(func.random()) \
            .limit(max_size)
        result.extend((await session.execute(stmt)).scalars())

    random.shuffle(result)
    return result
