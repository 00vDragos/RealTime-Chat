import uuid
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Header, Path

from backend.app.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession.

    Usage in a route or service:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            await db.execute(...)
    """
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


async def get_current_user_id(user_id: uuid.UUID = Header(...)) -> uuid.UUID:
    return user_id


async def get_current_conversation_id(conversation_id: uuid.UUID = Path(...)) -> uuid.UUID:
    return conversation_id
