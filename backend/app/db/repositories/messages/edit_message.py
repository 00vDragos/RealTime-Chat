import uuid
from datetime import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.messages import Message


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
