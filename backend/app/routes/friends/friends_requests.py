from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.dependencies import get_db, get_current_user_id
from app.schemas.friend_requests import FriendRequestCreate, FriendRequestOut
from app.services.friends.friend_requests import FriendRequestService

router = APIRouter()


@router.post("/friends/requests", response_model=FriendRequestOut)
async def send_friend_request(
    payload: FriendRequestCreate,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    try:
        fr = await FriendRequestService.send_request(db=db, from_user_id=user_id, to_email=payload.to_email)
        if not fr:
            raise HTTPException(status_code=500, detail="Unable to create friend request")
        return fr
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")