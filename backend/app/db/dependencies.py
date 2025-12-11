import uuid
from typing import AsyncGenerator

from fastapi import Depends, Path, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.services.auth import get_current_user


security = HTTPBearer()


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


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> uuid.UUID:
    """Resolve the current authenticated user's id from the access token.

    Requires an ``Authorization: Bearer <token>`` header. If the token is
    missing or invalid, raises 401/403 so protected routes cannot be
    accessed without logging in.
    """
    if not credentials or not credentials.scheme.lower() == "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    user = await get_current_user(token=credentials.credentials, db=db)
    return user.id


async def get_current_conversation_id(conversation_id: uuid.UUID = Path(...)) -> uuid.UUID:
    return conversation_id
