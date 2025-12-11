from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from app.schemas.auth import AccessTokenResponse, RefreshTokenRequest
from app.services.auth import refresh_access_token

router = APIRouter()

@router.post(
    "/auth/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh access token",
    description="Generate a new access token using a valid refresh token"
)
async def refresh(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> AccessTokenResponse:
    result = await refresh_access_token(
        refresh_token=data.refresh_token,
        db=db
    )
    return AccessTokenResponse(**result)

# Compatibility: serve /api path with same handler
@router.post(
    "/api/auth/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh access token [api]",
    description="Generate a new access token (api path)"
)
async def refresh_api(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> AccessTokenResponse:
    result = await refresh_access_token(
        refresh_token=data.refresh_token,
        db=db
    )
    return AccessTokenResponse(**result)