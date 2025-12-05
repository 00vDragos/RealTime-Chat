import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation_participants import ConversationsParticipants


async def get_participants(
    db: AsyncSession,
    conversation_id: uuid.UUID,
) -> List[ConversationsParticipants]:
    result = await db.execute(select(ConversationsParticipants).where(
        ConversationsParticipants.conversation_id == conversation_id
    ))

    return result.scalars().all()
