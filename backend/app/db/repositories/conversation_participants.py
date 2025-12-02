import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.conversation_participants import ConversationsParticipants


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
