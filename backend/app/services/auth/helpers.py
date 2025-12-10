import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_tokens import RefreshToken
from app.core.security import (
    generate_refresh_token,
    hash_refresh_token,
    create_refresh_token_expiry
)

async def create_refresh_token(
    user_id: uuid.UUID,
    db: AsyncSession
) -> str:
    """Create and store a refresh token for a user"""
    
    plain_token = generate_refresh_token()
    token_hash = hash_refresh_token(plain_token)
    
    new_refresh_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        expires_at=create_refresh_token_expiry()
    )
    
    db.add(new_refresh_token)
    await db.commit()
    
    return plain_token