import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError
from api.exceptions import NotFoundError
from api.persistence.models import Collection

logger = logging.getLogger(__name__)


async def remove_from_collection(
    _id: int,
    user_id: str,
    sessionmaker: async_sessionmaker[AsyncSession],
):
    async with sessionmaker() as session:
        stmt = select(Collection).where(Collection.book_id == _id).where(Collection.user_id == user_id)
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


async def get_in_collection(
    _id: int,
    user_id: str,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> bool:
    async with sessionmaker() as session:
        stmt = select(Collection) \
            .where(Collection.book_id == _id) \
            .where(Collection.user_id == user_id)
        result = await session.execute(stmt)
        result = result.scalar_one_or_none()
        return result is not None
