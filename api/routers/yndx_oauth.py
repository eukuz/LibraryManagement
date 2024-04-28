import base64
from typing import cast
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
import httpx
from pydantic import BaseModel
from api.config import YandexConfig
from api import di
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
    http_client: httpx.AsyncClient,
):
    secret_value = f'{oauth_cfg.client_id}:{oauth_cfg.client_secret.get_secret_value()}'.encode()
    token = base64.b64encode(secret_value).decode()
    token = f"Basic {token}"
    http_client.headers = {"Authorization": token}
    resp = await http_client.post(
        "https://oauth.yandex.ru/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
        },
    )
    logger.info(resp.request.headers["Authorization"])
    logger.info(resp.content)
    resp.raise_for_status()

    access_token: str | None = resp.json().get('access_token')
    if access_token is None:
        raise Exception("Expect 'access_token' field from Yandex OAuth")
    return access_token


class _UserData(BaseModel):
    display_name: str
    id: str


async def __get_user_data(
    access_token: str,
    http_client: httpx.AsyncClient,
) -> _UserData:
    token = f"OAuth {access_token}"
    http_client.headers = {"Authorization": token}
    resp = await http_client.get(
        "https://login.yandex.ru/info",
        params={"format": "json"},
        headers={
            "Authorization": f"OAuth {access_token}",
        },
    )
    logger.info(resp.request.headers["Authorization"])
    logger.info(resp.content)
    resp.raise_for_status()
    return _UserData.model_validate(resp.json())


@router.get("/redirect")
async def yndx_redirect_after_auth(
    code: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
    oauth_cfg: YandexConfig = Depends(di.yndx_oauth_cfg),
    sessionmaker: async_sessionmaker[AsyncSession] = Depends(di.sessionmaker),
    http_client: httpx.AsyncClient = Depends(di.http_client),
):
    if code is None and error is None:
        raise ValueError("Both code and error are null")
    if error is not None:
        msg = f"Error is not null: {error_description}"
        logger.error(msg)
        raise ValueError(msg)
    code = cast(str, code)

    access_token = await __get_access_token(code, oauth_cfg, http_client)
    user_data = await __get_user_data(access_token, http_client)
    user_id = await users.store_user_data(
        _id=user_data.id,
        fullname=user_data.display_name,
        sessionmaker=sessionmaker,
    )
    session_id = await users.create_new_session_for(user_id, sessionmaker)

    resp = RedirectResponse("https://ui.sqr.webrtc-thesis.ru/My_books")
    resp.set_cookie("SESSION_ID", session_id, domain="sqr.webrtc-thesis.ru")
    return resp
