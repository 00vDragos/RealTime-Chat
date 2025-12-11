from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.dependencies import get_db
from app.schemas.auth import UserResponse
from app.services.auth import get_current_user 
from typing import Annotated

router = APIRouter()
security = HTTPBearer()

@router.get(
    "/auth/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user",
    description="Retrieve details of the currently authenticated user"
)
async def get_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    token = credentials.credentials
    user = await get_current_user(token=token, db=db)
    return UserResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        provider=user.provider,
        provider_id=user.provider_id,
        created_at=user.created_at.isoformat() if user.created_at else None,
        updated_at=user.updated_at.isoformat() if user.updated_at else None,
        last_seen=user.last_seen.isoformat() if user.last_seen else None,
    )

# Compatibility: serve /api path with same handler
@router.get(
    "/api/auth/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user [api]",
    description="Retrieve current user (api path)"
)
async def get_user_api(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    token = credentials.credentials
    user = await get_current_user(token=token, db=db)
    return UserResponse(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        avatar_url=user.avatar_url,
        provider=user.provider,
        provider_id=user.provider_id,
        created_at=user.created_at.isoformat() if user.created_at else None,
        updated_at=user.updated_at.isoformat() if user.updated_at else None,
        last_seen=user.last_seen.isoformat() if user.last_seen else None,
    )
    