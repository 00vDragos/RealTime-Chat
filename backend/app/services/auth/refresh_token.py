from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.users import User
from app.models.refresh_tokens import RefreshToken
from app.core.security import (
    hash_refresh_token,
    is_token_expired,
    create_access_token
)

async def refresh_access_token(
        refresh_token: str,
        db: AsyncSession
    ) -> dict:
        """ Generate new access token using refresh token"""
        
        token_hash = hash_refresh_token(refresh_token)
        
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        stored_token = result.scalar_one_or_none()
        
        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
        if stored_token.revoked_at:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
        )
        
        if stored_token.expires_at and is_token_expired(stored_token.expires_at):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired"
            )
        
        result = await db.execute(
            select(User).where(User.id == stored_token.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        access_token = create_access_token(data={"id": str(user.id), "email": user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }