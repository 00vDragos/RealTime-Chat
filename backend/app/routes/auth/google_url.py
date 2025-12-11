from fastapi import APIRouter, status
from app.schemas.auth import GoogleAuthResponse 
from app.services.auth import get_google_auth_url

router = APIRouter()

@router.get(
    "/auth/google/url",
    response_model=GoogleAuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Google OAuth URL",
    description="Generate the Google OAuth2 authorization URL for user authentication"
)
async def google_auth_url() -> GoogleAuthResponse:
    url, state = await get_google_auth_url()
    return GoogleAuthResponse(url=url, state=state)

# Compatibility: serve /api path with same handler
@router.get(
    "/api/auth/google/url",
    response_model=GoogleAuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Google OAuth URL [api]",
    description="Generate Google OAuth URL (api path)"
)
async def google_auth_url_api() -> GoogleAuthResponse:
    url, state = await get_google_auth_url()
    return GoogleAuthResponse(url=url, state=state)