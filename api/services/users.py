from uuid import uuid4
from venv import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from api.persistence.models import User, UserSession


class UserData(BaseModel):
    id: str
    fullname: str


async def get_user_data(
    session_id: str,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> UserData | None:
    async with sessionmaker() as session:
        stmt = select(UserSession).where(UserSession.session_id == session_id)
        result = await session.execute(stmt)
        user_session = result.scalars().all()
        if len(user_session) == 0:
            return None
        user = user_session[0].user
        return UserData(fullname=user.fullname, id=user.id)


async def store_user_data(
    _id: str,
    fullname: str,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> str:
    async with sessionmaker() as session:
        user = User(id=_id, fullname=fullname)
        session.add(user)
        try:
            await session.commit()
        except IntegrityError:
            logger.info("User with id '%s' already exists", _id)

    return _id


async def create_new_session_for(
    user_id: str,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> str:
    session_id = str(uuid4())
    async with sessionmaker() as session:
        user_session = UserSession(user_id=user_id, session_id=session_id)
        session.add(user_session)
        await session.commit()
    return session_id
