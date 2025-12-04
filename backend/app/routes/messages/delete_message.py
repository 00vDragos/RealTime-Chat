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


router = APIRouter()


@router.delete("/conversations/{conversation_id}/{message_id}/delete", response_model=MessageDeletionRead)
async def delete_message(
    message_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    conversation_id: uuid.UUID = Depends(get_current_conversation_id),
):
    try:
        deletion = await delete_message_service(
            db=db,
            message_id=message_id,
            conversation_id=conversation_id,
            user_id=user_id,
        )

        if not deletion:
            raise HTTPException(status_code=400, detail="Unable to delete message")

        return deletion

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
