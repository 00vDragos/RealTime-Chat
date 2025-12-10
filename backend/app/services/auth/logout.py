from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.refresh_tokens import RefreshToken
from app.core.security import hash_refresh_token

async def logout_user(
    refresh_token: str,
    db: AsyncSession
) -> None:
    """Lougout user by invalidation of token"""
    
    token_hash = hash_refresh_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored_token = result.scalar_one_or_none()
    if not stored_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found"
        )
    
    stored_token.revoked_at = datetime.now(timezone.utc)
    await db.commit()