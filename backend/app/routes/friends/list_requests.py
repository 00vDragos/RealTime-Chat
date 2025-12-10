from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.dependencies import get_db, get_current_user_id
from app.services.friends.friend_requests import FriendRequestService
from app.schemas.friend_requests import FriendRequestOut

router = APIRouter()


@router.get("/friends/requests", response_model=list[FriendRequestOut])
async def list_requests(direction: str | None = None, db: AsyncSession = Depends(get_db), user_id: uuid.UUID = Depends(get_current_user_id)):
    try:
        results = await FriendRequestService.list_requests(db=db, user_id=user_id, direction=direction)
        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
