import uuid
from datetime import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message_deletions import MessageDeletion
from app.models.messages import Message


async def delete_message(
    db: AsyncSession,
    message_id: uuid.UUID,
    user_id: uuid.UUID
) -> MessageDeletion:
    deletion = MessageDeletion(
        message_id=message_id,
        user_id=user_id,
        deleted_at=datetime.utcnow()
    )
    db.add(deletion)
    await db.execute(
        update(Message)
        .where(Message.id == message_id)
        .values(
            deleted_for_everyone=True
        )
    )
    await db.commit()
    return deletion
