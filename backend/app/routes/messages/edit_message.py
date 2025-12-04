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


router = APIRouter()


@router.put("/conversations/{conversation_id}/{message_id}/edit", response_model=MessageRead)
async def edit_message(
    message_id: uuid.UUID,
    new_body: str,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    conversation_id: uuid.UUID = Depends(get_current_conversation_id)
):
    try:
        updated = await edit_message_service(
            db=db,
            message_id=message_id,
            conversation_id=conversation_id,
            user_id=user_id,
            new_body=new_body,
        )

        if not updated:
            raise HTTPException(status_code=400, detail="Unable to edit message")

        return updated

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
