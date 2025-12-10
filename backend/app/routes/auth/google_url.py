from fastapi import APIRouter
from app.schemas.auth import GoogleAuthResponse 
from app.services.auth import get_google_auth_url

router = APIRouter()

@router.get("/auth/google/url",
            response_model=GoogleAuthResponse,
            summary="Get Google OAuth URL",
            description="Generate the Google OAuth2 authorization URL for user authentication"
)
async def google_auth_url() -> GoogleAuthResponse:
    url, state = await get_google_auth_url()
    return GoogleAuthResponse(url=url, state=state)