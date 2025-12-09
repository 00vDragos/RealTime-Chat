from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.dependencies import get_db, get_current_user_id
from app.services.friends.friend_requests import FriendRequestService

router = APIRouter()


@router.delete("/friends/requests/{request_id}")
async def cancel_request(request_id: uuid.UUID, db: AsyncSession = Depends(get_db), user_id: uuid.UUID = Depends(get_current_user_id)):
    try:
        await FriendRequestService.cancel_request(db=db, user_id=user_id, request_id=request_id)
        return {"detail": "cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
