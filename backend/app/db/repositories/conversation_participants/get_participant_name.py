import uuid

from sqlalchemy import select
from app.models.users import User
from sqlalchemy.ext.asyncio import AsyncSession


async def get_participant_name(
    db: AsyncSession,
    user_id: uuid.UUID
) -> str:
    result = await db.execute(
        select(User.display_name).where(User.id == user_id)
    )
    return result.scalar()