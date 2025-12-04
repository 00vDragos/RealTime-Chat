import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.messages import Message


async def create_message(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    sender_id: uuid.UUID,
    body: str
) -> Message:
    msg = Message(
        id=uuid.uuid4(),
        conversation_id=conversation_id,
        sender_id=sender_id,
        body=body,
        created_at=datetime.utcnow(),
        delivered_at={},
        seen_at={},
        edited_at=None,
        deleted_for_everyone=False
    )

    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    return msg