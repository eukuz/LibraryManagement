import base64
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from api.config import YandexConfig
from api import di
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
import logging

from api.services import users


router = APIRouter()
logger = logging.getLogger(__name__)


class OAuthModel(BaseModel):
    login: str
    id: str


@router.get("/authenticate")
async def authenticate_user(oauth_cfg: YandexConfig = Depends(di.yndx_oauth_cfg)):
    url = "https://oauth.yandex.ru/authorize?" \
        f"response_type=code" \
        f"&client_id={oauth_cfg.client_id}"
    return RedirectResponse(url=url)


async def __get_access_token(
    code: str,
    oauth_cfg: YandexConfig,
):
    token = base64.b64encode(f'{oauth_cfg.client_id}:{oauth_cfg.client_secret.get_secret_value()}'.encode()).decode()
    token = f"Basic {token}"
    client = AsyncClient(headers={"Authorization": token})
    async with client:
        resp = await client.post(
            "https://oauth.yandex.ru/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
            },
        )
        logger.info(resp.request.headers["Authorization"])
        logger.info(resp.content)
        resp.raise_for_status()

        access_token = resp.json().get('access_token')
        if access_token is None:
            raise Exception("Expect 'access_token' field from Yandex OAuth")
        return access_token


class __UserData(BaseModel):
    display_name: str
    id: str


async def __get_user_data(access_token: str) -> __UserData:
    token = f"OAuth {access_token}"
    client = AsyncClient(headers={"Authorization": token})
    async with client:
        resp = await client.get(
            "https://login.yandex.ru/info",
            params={"format": "json"},
            headers={
                "Authorization": f"OAuth {access_token}",
            },
        )
        logger.info(resp.request.headers["Authorization"])
        logger.info(resp.content)
        resp.raise_for_status()
        return __UserData.model_validate(resp.json())


@router.get("/redirect")
async def yndx_redirect_after_auth(
    code: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    oauth_cfg: YandexConfig = Depends(di.yndx_oauth_cfg),
    sessionmaker: async_sessionmaker[AsyncSession] = Depends(di.sessionmaker)
):
    if code is None and error is None:
        raise Exception("Both code and error are null")
    if error is not None:
        msg = f"Error is not null: {error_description}"
        logger.error(msg)
        raise Exception(msg)
    if code is None:
        msg = "Code is null"
        logger.error(msg)
        raise Exception(msg)

    access_token = await __get_access_token(code, oauth_cfg)
    user_data = await __get_user_data(access_token)
    user_id = await users.store_user_data(
        _id=user_data.id,
        fullname=user_data.display_name,
        sessionmaker=sessionmaker,
    )
    session_id = await users.create_new_session_for(user_id, sessionmaker)

    resp = RedirectResponse("/")
    resp.set_cookie("SESSION_ID", session_id)
    return resp
