from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import uuid

from app.models.users import User
from app.core.security import decode_access_token

async def get_current_user(
    token: str,
    db: AsyncSession) -> User:
    """Retrieve current user from access token"""
    
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
            
    user_id: str = payload.get("id")
        
    if user_id is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token payload"
    )
        
    try:
        result = await db.execute(
            select(User).where(User.id == uuid.UUID(user_id))
            )
        user = result.scalar_one_or_none()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )
    
    return user