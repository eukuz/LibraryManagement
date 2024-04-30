import os
from typing import Any, AsyncGenerator
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from api.config import YandexConfig
from api.main import create_app
from api.persistence.models import Base, Genre, Author
from api.services import books, users
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from api import di


@pytest.fixture(scope='session')
def db_path() -> str:
    return ":memory:"


@pytest.fixture(scope='session')
def session_id() -> str:
    return "aboba"


@pytest.fixture(scope='session')
def user_id() -> str:
    return "1"


@pytest.fixture(scope='session')
def set_envs():
    try:
        os.environ['YNDX_CLIENT_ID'] = '1'
        os.environ['YNDX_CLIENT_SECRET'] = '1'
        yield
    finally:
        try:
            del os.environ['YNDX_CLIENT_ID']
            del os.environ['YNDX_CLIENT_SECRET']
        except KeyError:
            pass


@pytest.fixture
def yndx_config(set_envs):
    return YandexConfig()  # type: ignore


@pytest.fixture
def app(yndx_config, db_path) -> FastAPI:
    return create_app(db_path)


@pytest_asyncio.fixture
async def sessionmaker(db_path) -> AsyncGenerator[async_sessionmaker[AsyncSession], Any]:
    yield await di.init_db(db_path)


@pytest_asyncio.fixture(autouse=True)
async def set_session_id(
    user_id,
    sessionmaker: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[str, Any]:
    async with sessionmaker() as session:
        conn = await session.connection()
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await users.store_user_data(user_id, "aboba", sessionmaker)
        session.add(Genre(name="genre1"))
        session.add(Author(fullname="author1"))
        session.add(Genre(name="genre2"))
        session.add(Author(fullname="author2"))
        await session.commit()
        await books.add_book("1", "author1", "genre1", 100, sessionmaker)
        await books.add_book("2", "author2", "genre2", 200, sessionmaker)
    session_id = await users.create_new_session_for(user_id, sessionmaker)

    yield session_id


@pytest.fixture
def client(app, set_session_id) -> TestClient:
    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {set_session_id}"
    return client
