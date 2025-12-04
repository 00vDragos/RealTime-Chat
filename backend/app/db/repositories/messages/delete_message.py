import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.message_deletions import MessageDeletion


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
    await db.commit()
    return deletion
