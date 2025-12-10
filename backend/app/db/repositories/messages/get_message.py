import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.messages import Message


async def get_message(db: AsyncSession, message_id: uuid.UUID) -> Message | None:
    result = await db.execute(select(Message).where(Message.id == message_id))
    return result.scalars().first()
