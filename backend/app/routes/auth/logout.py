from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from app.schemas.auth import MessageResponse, LogoutRequest
from app.services.auth import logout_user

router = APIRouter()

@router.post("/auth/logout",
             response_model=MessageResponse,
             summary="Logout user",
             description="Logout user by invalidating the refresh token")
async def logout(
    data: LogoutRequest,
    db: AsyncSession = Depends(get_db)) -> MessageResponse:
    
    await logout_user(
        refresh_token=data.refresh_token,
        db=db
    )
    return MessageResponse(message="Logout successful")