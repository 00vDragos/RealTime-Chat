from fastapi import APIRouter, Depends
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db, get_current_user_id
from app.services.friendships.list_friends import list_friends_service
from app.schemas.users import UserRead

router = APIRouter(prefix="/api/friends", tags=["friends"])

@router.get("/list", response_model=List[UserRead])
async def list_my_friends(
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    friends = await list_friends_service(db, user_id)
    return friends
