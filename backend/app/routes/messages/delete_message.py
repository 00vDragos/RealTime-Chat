from fastapi import APIRouter, Depends, HTTPException
import uuid

from app.db.dependencies import (
    get_db,
    get_current_user_id,
    get_current_conversation_id,
)
from app.services.messages.delete_message import delete_message_service
from app.schemas.message_deletions import MessageDeletionRead
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.conversation_participants.is_participant import is_conversation_participant_service
from app.db.repositories.conversation_participants.get_all_participants import get_participants
from app.websocket.manager import manager
from app.services.conversation_participants.get_participant_name import get_participant_name_service

router = APIRouter()


@router.delete("/conversations/{conversation_id}/messages/{message_id}", response_model=MessageDeletionRead)
async def delete_message(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    conversation_id: uuid.UUID = Depends(get_current_conversation_id),
):
    try:
        if not await is_conversation_participant_service(db, conversation_id, user_id):
            raise HTTPException(status_code=403, detail="Not a participant")

        deletion = await delete_message_service(
            db=db,
            message_id=message_id,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not deletion:
            raise HTTPException(status_code=400, detail="Unable to delete message")

        deletion.sender_name = await get_participant_name_service(db, deletion.sender_id)

        participants = await get_participants(db, conversation_id)
        participant_ids = [str(p.user_id) for p in participants]

        await manager.broadcast(
            participant_ids,
            {
                "event": "message_deleted",
                "conversation_id": str(conversation_id),
                "message_id": str(message_id),
                "deleted_by": str(user_id),
                "deletor_name": deletion.sender_name,
            },
        )

        return deletion

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
