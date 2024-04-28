from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel
from api import di
from api.services import collections
from api.models.api import CollectionItem


router = APIRouter()


class CollectionResponse(BaseModel):
    books: list[CollectionItem]


@router.get("/")
async def get_collection(
    user_id=Security(di.get_user_id),
    sessionmaker=Depends(di.sessionmaker),
) -> CollectionResponse:
    return CollectionResponse(books=await collections.get_collection(user_id, sessionmaker))
