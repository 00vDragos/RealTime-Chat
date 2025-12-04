import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.messages import Message


async def get_last_message_id(
    db: AsyncSession,
    conversation_id: uuid.UUID
) -> Optional[uuid.UUID]:
    result = await db.execute(
        select(Message.id)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(1)
    )

    return result.scalar_one_or_none()