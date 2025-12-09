from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.dependencies import get_db, get_current_user_id
from app.services.friends.friend_requests import FriendRequestService
from app.schemas.users import UserOut

router = APIRouter()


@router.get("/friends", response_model=list[UserOut])
async def list_friends(db: AsyncSession = Depends(get_db), user_id: uuid.UUID = Depends(get_current_user_id)):
    try:
        results = await FriendRequestService.list_friends(db=db, user_id=user_id)
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
