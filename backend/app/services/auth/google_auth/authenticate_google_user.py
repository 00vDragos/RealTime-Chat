from datetime import datetime, timezone
from typing import Optional
from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import uuid

from app.models.users import User
from app.core.config import settings
from app.core.security import create_access_token
from app.services.auth.helpers import create_refresh_token

async def authenticate_google_user(
    code: str,
    db: AsyncSession
) -> dict:
    """Authenticate user with Google OAuth using automatic discovery"""
    async with AsyncOAuth2Client(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        scope=settings.GOOGLE_SCOPES
    ) as client:
        
        try:
            token = await client.fetch_token(
                url="https://oauth2.googleapis.com/token", 
                code=code,
                grant_type="authorization_code"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange authorization code: {str(e)}"
            )
        
        try:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token['access_token']}"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Google API returned {response.status_code}: {response.text}")
            
            
            user_info = response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info: {str(e)}"
            )
        
        google_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")
        email_verified = user_info.get("verified_email", False)
        
        if not google_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user data received from Google"
            )
        
        if not email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google account email is not verified. Please verify your email with Google first."
            )
        
        user = await _find_or_create_user(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
            db=db
        )
        
        access_token = create_access_token(
            data={
                "id": str(user.id),
                "email": user.email
            }
        )
        
        refresh_token = await create_refresh_token(user.id, db)
        
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
    
async def _find_or_create_user(
    google_id: str,
    email: str,
    name: Optional[str],
    picture: Optional[str],
    db: AsyncSession) -> User:
    """Find existing registered user with Google account or create a new one"""
    
    result = await db.execute(
        select(User).where(User.provider_id == google_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.display_name = name or user.display_name
        user.avatar_url = picture or user.avatar_url
        user.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(user)
        return user
    
    result = await db.execute(
        select(User).where(User.email == email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.provider == 'local' and existing_user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists. Please login using email and password."
            )
        
        existing_user.provider = 'google'
        existing_user.provider_id = google_id
        existing_user.display_name = name or existing_user.display_name
        existing_user.avatar_url = picture or existing_user.avatar_url
        existing_user.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing_user)
        return existing_user
    
    new_user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=None,
        display_name=name,
        avatar_url=picture,
        provider='google',
        provider_id=google_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user