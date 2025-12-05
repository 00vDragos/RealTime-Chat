from fastapi import APIRouter, Depends, HTTPException
import uuid
from typing import Sequence

from app.db.dependencies import (
    get_db,
    get_current_user_id,
    get_current_conversation_id,
)
from app.services.conversation_participants.is_participant import (
    is_conversation_participant_service,
)
from app.services.messages.get_messages import get_messages_service
from app.schemas.messages import MessageRead
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.get("/conversations/{conversation_id}/messages", response_model=Sequence[MessageRead])
async def get_messages(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    conversation_id: uuid.UUID = Depends(get_current_conversation_id),
):
    try:
        if not await is_conversation_participant_service(db, conversation_id, user_id):
            raise HTTPException(status_code=403, detail="Not a participant")

        msgs = await get_messages_service(
            db=db,
            conversation_id=conversation_id,
            limit=limit,
            offset=offset)

        if msgs is None:
            raise HTTPException(status_code=400, detail="Unable to get messages")

        return msgs

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
