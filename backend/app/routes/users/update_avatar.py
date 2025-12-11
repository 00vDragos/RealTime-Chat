from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl
from typing import Annotated

from app.db.dependencies import get_db
from app.services.auth import get_current_user
from app.schemas.auth import UserResponse

router = APIRouter()


class UpdateAvatarRequest(BaseModel):
    avatar_url: HttpUrl


@router.patch(
    "/api/users/me/avatar",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user's avatar URL",
    description="Set the avatar URL for the authenticated user"
)
async def update_avatar(
    payload: UpdateAvatarRequest,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    token = credentials.credentials
    user = await get_current_user(token=token, db=db)

    # Update avatar URL
    user.avatar_url = str(payload.avatar_url)
    try:
        await db.flush()
        await db.commit()
        # Ensure refreshed attributes are loaded in async session
        await db.refresh(user)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update avatar") from e

    return UserResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        provider=user.provider,
        provider_id=user.provider_id,
        created_at=user.created_at.isoformat() if user.created_at else None,
        updated_at=user.updated_at.isoformat() if user.updated_at else None,
    )
