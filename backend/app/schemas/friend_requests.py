from pydantic import BaseModel, EmailStr
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime


FriendRequestStatus = Literal["pending", "accepted", "declined", "canceled"]


class FriendRequestCreate(BaseModel):
    to_email: EmailStr


class FriendRequestOut(BaseModel):
    id: UUID
    from_user_id: UUID
    to_user_id: UUID
    status: FriendRequestStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class FriendRequestUpdate(BaseModel):
    status: FriendRequestStatus