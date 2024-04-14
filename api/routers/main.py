from fastapi import APIRouter, Depends, Security
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from api import di
import logging


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def main_page(
    user_id: str = Security(di.get_user_id),
    sessionmaker: async_sessionmaker[AsyncSession] = Depends(di.sessionmaker),
):
    pass
