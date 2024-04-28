from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from api.config import YandexConfig
from api.persistence.models import Base
from api.services import users
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event
import logging


logger = logging.getLogger(__name__)


_sessionmaker: async_sessionmaker[AsyncSession] | None = None
_yndx_cfg: YandexConfig | None = None

security = HTTPBearer(auto_error=False)


async def sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        raise Exception("_sessionmaker is not initialized")
    return _sessionmaker


def yndx_oauth_cfg() -> YandexConfig:
    global _yndx_cfg
    if _yndx_cfg is None:
        _yndx_cfg = YandexConfig()  # type: ignore
    return _yndx_cfg


async def init_db(db_path: str) -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is not None:
        return _sessionmaker

    async_engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=True)

    @event.listens_for(async_engine.sync_engine, "connect")
    def _(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        logger.info("Set pragma")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    _sessionmaker = async_sessionmaker(
        async_engine,
        expire_on_commit=False,
    )

    return _sessionmaker


async def http_client():
    async with httpx.AsyncClient() as client:
        yield client


async def __cookie_checker(request: Request):
    if (session_id := request.cookies.get("SESSION_ID")) is not None:
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=session_id)


async def __get_user_data(
    sessionmaker=Depends(sessionmaker),
    creds: HTTPAuthorizationCredentials | None = Depends(security),
    cookie_creds: HTTPAuthorizationCredentials | None = Depends(__cookie_checker),
) -> users.UserData:
    if creds is None:
        creds = cookie_creds
    if creds is None:
        raise HTTPException(status_code=401)
    userdata = await users.get_user_data(creds.credentials, sessionmaker)
    if userdata is None:
        logger.warning("Cannot find user for session '%s'", creds.credentials)
        raise HTTPException(status_code=401)
    return userdata


async def get_user_id(userdata=Depends(__get_user_data)):
    return userdata.id
