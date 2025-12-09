from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.dependencies import get_db, get_current_user_id
from app.services.friends.friend_requests import FriendRequestService

router = APIRouter()


@router.delete("/friends/{friend_id}")
async def remove_friend(friend_id: uuid.UUID, db: AsyncSession = Depends(get_db), user_id: uuid.UUID = Depends(get_current_user_id)):
    try:
        await FriendRequestService.remove_friend(db=db, user_id=user_id, friend_id=friend_id)
        return {"detail": "removed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
