import logging
from operator import and_
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from api.exceptions import NotFoundError
from api.models.api import CollectionItem
from api.persistence.models import Book, BookProgress, Collection, User

logger = logging.getLogger(__name__)


async def remove_from_collection(
    _id: int,
    user_id: str,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    async with sessionmaker() as session:
        stmt = select(Collection) \
            .where(Collection.book_id == _id) \
            .where(Collection.user_id == user_id)
        rows_count = 0
        for row in (await session.execute(stmt)).scalars():
            await session.delete(row)
            rows_count += 1
        if rows_count == 0:
            raise NotFoundError
        await session.commit()


async def add_to_collection(
    _id: int,
    user_id: str,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    async with sessionmaker() as session:
        session.add(Collection(book_id=_id, user_id=user_id))
        try:
            await session.commit()
        except IntegrityError as e:
            if "FOREIGN KEY constraint failed" in str(e):
                raise NotFoundError from e
            raise


async def set_in_collection(
    _id: int,
    user_id: str,
    add: bool,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    if add:
        await add_to_collection(_id, user_id, sessionmaker)
    else:
        await remove_from_collection(_id, user_id, sessionmaker)


async def get_collection(
    user_id: str,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> list[CollectionItem]:
    async with sessionmaker() as session:
        stmt = select(Book, BookProgress.read_pages, Collection.created_at) \
            .join(BookProgress, isouter=True) \
            .join(
                Collection,
                onclause=and_(
                    Collection.book_id == Book.id,
                    Collection.user_id == select(User.id).where(User.id == user_id).scalar_subquery(),
                ),
            )
        books = list(await session.execute(stmt))
        result: list[CollectionItem] = []
        for (book, read_pages, created_at) in books:
            result.append(CollectionItem(
                id=book.id,
                title=book.title,
                author=book.author_id,
                genre=book.genre_name,
                read_pages=read_pages or 0,
                total_pages=book.pages,
            ))
        return result
