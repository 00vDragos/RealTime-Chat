from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an AsyncSession.

    Usage in a route or service:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            await db.execute(...)
    """
    async with AsyncSessionLocal() as session:
        yield session
