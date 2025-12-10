from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from app.schemas.auth import TokenResponse, UserLogin
from app.services.auth import login_user

router = APIRouter()

@router.post("/auth/login",
             response_model=TokenResponse,
             summary="Login user",
             description="Authenticate user with email and password"
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db)) -> TokenResponse:
    
    result = await login_user(
        email=data.email,
        password=data.password,
        db=db
    )
    return TokenResponse(**result)
