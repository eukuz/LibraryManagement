from fastapi import APIRouter, Depends, Security
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from api import di
import logging

from api.persistence.models import UserSession


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def main_page(
    user_id: str = Security(di.get_user_id),
    sessionmaker: async_sessionmaker[AsyncSession] = Depends(di.sessionmaker),
):
    async with sessionmaker() as session:
        stmt = select(UserSession).where(UserSession.user_id == user_id)
        sessions = (await session.execute(stmt)).scalars()
        session_id = None
        for session in sessions:
            session_id = session.session_id
    return JSONResponse({"session_id": session_id})
