import uuid
from datetime import datetime
from typing import Sequence, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.messages import Message
from backend.app.models.message_deletions import MessageDeletion


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

async def edit_message(
    db: AsyncSession,
    message_id: uuid.UUID,
    new_body: str
) -> Message:
    result = await db.execute(
        update(Message)
        .where(Message.id == message_id)
        .values(body=new_body, edited_at=datetime.utcnow())
        .returning(Message)
    )

    await db.commit()
    return result.scalar_one()


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
