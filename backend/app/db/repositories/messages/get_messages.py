import uuid
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.messages import Message


async def get_messages(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0
) -> Sequence[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )

    return result.scalars().all()
