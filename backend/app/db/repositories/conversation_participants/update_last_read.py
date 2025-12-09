import uuid
from datetime import datetime

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.conversation_participants import ConversationsParticipants
from app.models.messages import Message


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

    participant = result.scalar_one()

    now = datetime.utcnow().isoformat()
    user_key = str(user_id)

    msgs_result = await db.execute(
        select(Message).where(Message.conversation_id == conversation_id)
    )
    messages = msgs_result.scalars().all()

    for msg in messages:
        seen_map = msg.seen_at or {}

        if user_key not in seen_map:
            seen_map[user_key] = now
            msg.seen_at = seen_map

    await db.commit()

    return participant
