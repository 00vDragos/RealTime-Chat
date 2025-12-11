from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from app.schemas.auth import GoogleAuthRequest, TokenResponse 
from app.services.auth import authenticate_google_user

router = APIRouter()

@router.get(
    "/api/auth/google/callback",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Handle Google OAuth callback (Browser Redirect)",
    description="Handles Google OAuth2 redirect with authorization code"
)
async def google_callback_get(
    code: str = Query(description="Authorization code from Google"),
    state: str = Query(description="State parameter for CSRF protection"),
    db: AsyncSession = Depends(get_db)
)-> TokenResponse:
    
    result = await authenticate_google_user(code=code, db=db)
    return TokenResponse(**result)

# Backward-compatible path without /api prefix
@router.get(
    "/auth/google/callback",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Handle Google OAuth callback (Browser Redirect) [compat]",
    description="Alias path without /api prefix for legacy callers"
)
async def google_callback_get_compat(
    code: str = Query(description="Authorization code from Google"),
    state: str = Query(description="State parameter for CSRF protection"),
    db: AsyncSession = Depends(get_db)
)-> TokenResponse:
    result = await authenticate_google_user(code=code, db=db)
    return TokenResponse(**result)

@router.post("/api/auth/google/callback",
             response_model=TokenResponse,
             summary="Handle Google OAuth callback",
             description="Handle the Google OAuth2 callback and authenticate the user")
async def google_callback(
    data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)) -> TokenResponse:
    
    results = await authenticate_google_user(
        code=data.code,
        db=db
    )
    return TokenResponse(**results)

# Backward-compatible POST alias without /api prefix
@router.post(
    "/auth/google/callback",
    response_model=TokenResponse,
    summary="Handle Google OAuth callback [compat]",
    description="Alias path without /api prefix for legacy callers"
)
async def google_callback_compat(
    data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    results = await authenticate_google_user(
        code=data.code,
        db=db
    )
    return TokenResponse(**results)