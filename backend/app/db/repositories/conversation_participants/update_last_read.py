import uuid
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.conversation_participants import ConversationsParticipants


async def update_last_read(
    db: AsyncSession,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    message_id: uuid.UUID
) -> ConversationsParticipants:
    result = await db.execute(
        update(ConversationsParticipants)
        .where(
            ConversationsParticipants.conversation_id == conversation_id,
            ConversationsParticipants.user_id == user_id
        )
        .values(last_read_message_id=message_id)
        .returning(ConversationsParticipants)
    )

    await db.commit()

    return result.scalar_one()
