from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.dependencies import get_db, get_current_user_id
from app.schemas.friend_requests import FriendRequestUpdate, FriendRequestOut
from app.services.friends.friend_requests import FriendRequestService

router = APIRouter()


@router.post("/friends/requests/{request_id}/respond", response_model=FriendRequestOut)
async def respond_request(request_id: uuid.UUID, payload: FriendRequestUpdate, db: AsyncSession = Depends(get_db), user_id: uuid.UUID = Depends(get_current_user_id)):
    try:
        fr = await FriendRequestService.respond_request(db=db, user_id=user_id, request_id=request_id, status=payload.status)
        return fr
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

# Backward-compatible alias with /api prefix
@router.post("/api/friends/requests/{request_id}/respond", response_model=FriendRequestOut)
async def respond_request_api(request_id: uuid.UUID, payload: FriendRequestUpdate, db: AsyncSession = Depends(get_db), user_id: uuid.UUID = Depends(get_current_user_id)):
    try:
        fr = await FriendRequestService.respond_request(db=db, user_id=user_id, request_id=request_id, status=payload.status)
        return fr
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
