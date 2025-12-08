from fastapi import APIRouter, Depends, HTTPException
import uuid

from app.db.dependencies import (
    get_db,
    get_current_user_id,
)

from app.db.dependencies import get_current_conversation_id
from app.services.messages.edit_message import edit_message_service
from app.schemas.messages import MessageRead
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.conversation_participants.is_participant import is_conversation_participant_service
from app.db.repositories.conversation_participants.get_all_participants import get_participants
from app.websocket.manager import manager

router = APIRouter()


@router.put("/conversations/{conversation_id}/messages/{message_id}", response_model=MessageRead)
async def edit_message(
    message_id: uuid.UUID,
    new_body: str,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    conversation_id: uuid.UUID = Depends(get_current_conversation_id)
):
    try:
        if not await is_conversation_participant_service(db, conversation_id, user_id):
            raise HTTPException(status_code=403, detail="Not a participant")

        updated = await edit_message_service(
            db=db,
            message_id=message_id,
            conversation_id=conversation_id,
            user_id=user_id,
            new_body=new_body,
        )

        if not updated:
            raise HTTPException(status_code=400, detail="Unable to edit message")

        participants = await get_participants(db, conversation_id)
        participant_ids = [str(p.user_id) for p in participants]

        await manager.broadcast(
            participant_ids,
            {
                "event": "message_edited",
                "conversation_id": str(conversation_id),
                "message": {
                    "id": str(updated.id),
                    "body": updated.body,
                    "sender_id": str(updated.sender_id),
                },
            },
        )

        return updated

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
