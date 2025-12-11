from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.users import User
from app.core.security import verify_password, create_access_token
from .helpers import create_refresh_token
from app.services.ai.openai_bot import ensure_user_has_openai_friendship

async def login_user(
        email: str,
        password: str,
        db: AsyncSession
    ) -> dict:
        """Authenticate user with email and password"""
        
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This account uses {user.provider} authentication. Please sign in with {user.provider}."
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        access_token = create_access_token(data={"id": str(user.id), "email": user.email})
        
        refresh_token = await create_refresh_token(user.id, db)
        await ensure_user_has_openai_friendship(db, user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url,
                "provider": user.provider,
                "provider_id": user.provider_id,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat()
            }
        }