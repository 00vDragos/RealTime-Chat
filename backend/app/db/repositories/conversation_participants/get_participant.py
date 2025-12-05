import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation_participants import ConversationsParticipants


async def get_participant(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID
) -> ConversationsParticipants:
    result = await db.execute(
        select(ConversationsParticipants)
        .where(
            ConversationsParticipants.conversation_id == conversation_id,
            ConversationsParticipants.user_id == user_id
        )
    )

    return result.scalar_one()