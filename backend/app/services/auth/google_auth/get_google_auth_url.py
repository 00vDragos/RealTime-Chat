from authlib.integrations.httpx_client import AsyncOAuth2Client
from app.core.config import settings


async def get_google_auth_url() -> tuple[str, str]:
    """Generate Google OAuth2 authorization URL """
    
    async with AsyncOAuth2Client(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
        scope=settings.GOOGLE_SCOPES,
    ) as client:
        
        authorization_url, state = client.create_authorization_url(
            url="https://accounts.google.com/o/oauth2/v2/auth", 
            access_type="offline",  
            prompt="consent"  
        )
        
        return authorization_url, state
