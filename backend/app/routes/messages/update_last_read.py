from fastapi import APIRouter, Depends, HTTPException
import uuid

from app.db.dependencies import (
    get_db,
    get_current_user_id,
    get_current_conversation_id,
)
from app.services.conversation_participants.is_participant import (
    is_conversation_participant_service,
)
from app.services.conversation_participants.update_last_read import update_last_read_service
from app.schemas.conversation_participants import ConversationParticipantRead
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.post("/conversations/{conversation_id}/read", response_model=ConversationParticipantRead)
async def update_last_read(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    conversation_id: uuid.UUID = Depends(get_current_conversation_id),
):
    try:
        if not await is_conversation_participant_service(db, conversation_id, user_id):
            raise HTTPException(status_code=403, detail="Not a participant")

        updated = await update_last_read_service(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id,
            message_id=message_id
        )

        if not updated:
            raise HTTPException(status_code=400, detail="Unable to update last read")

        return updated

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
