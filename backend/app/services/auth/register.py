from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import uuid

from app.models.users import User
from app.core.security import hash_password, create_access_token
from .helpers import create_refresh_token

async def register_user(
        email: str,
        password: str,
        display_name: Optional[str],
        db: AsyncSession
    ) -> dict:
        """Register a new user with email and password"""
        
        result = await db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered."
            )
        
        hashed_pw = hash_password(password)
        
        new_user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hashed_pw,
            display_name=display_name,
            provider='local',
            provider_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc))
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        access_token = create_access_token(data={"id": str(new_user.id), "email": new_user.email})
        
        refresh_token = await create_refresh_token(new_user.id, db)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": str(new_user.id),
                "email": new_user.email,
                "display_name": new_user.display_name,
                "avatar_url": new_user.avatar_url,
                "provider": new_user.provider,
                "provider_id": new_user.provider_id,
                "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
                "updated_at": new_user.updated_at.isoformat()
            }
        }