import uuid

from sqlalchemy import select
from app.models.users import users
from sqlalchemy.ext.asyncio import AsyncSession


async def get_participant_name(
    db: AsyncSession,
    user_id: uuid.UUID
) -> str:
    result = await db.execute(
        select(users.display_name).where(users.id == user_id)
    )
    return result.scalar()