from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from app.schemas.auth import TokenResponse, UserRegister
from app.services.auth import register_user

router = APIRouter()

@router.post(
    "/auth/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user with email and password"
)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    result = await register_user(
        email=data.email,
        password=data.password,
        display_name=data.display_name,
        db=db
    )
    return TokenResponse(**result)

# Compatibility: serve /api path with same handler
@router.post(
    "/api/auth/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user [api]",
    description="Register a new user (api path)"
)
async def register_api(
    data: UserRegister,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    result = await register_user(
        email=data.email,
        password=data.password,
        display_name=data.display_name,
        db=db
    )
    return TokenResponse(**result)