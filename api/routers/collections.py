from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel
from api import di


router = APIRouter()


class CollectionItem(BaseModel):
    title: str
    author: str
    genre: str

    progress: int
    total_pages: int


class CollectionResponse(BaseModel):
    books: list[CollectionItem]


@router.get("/")
async def get_collection(
    user_id=Security(di.get_user_id),
    sessionmaker=Depends(di.sessionmaker),
):
    pass
