from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime


FriendRequestStatus = Literal["pending", "accepted", "declined", "canceled"]


class FriendRequestCreate(BaseModel):
    to_email: EmailStr


class FriendRequestUser(BaseModel):
    id: UUID
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FriendRequestOut(BaseModel):
    id: UUID
    from_user_id: UUID
    to_user_id: UUID
    status: FriendRequestStatus
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    from_user: Optional[FriendRequestUser] = None
    to_user: Optional[FriendRequestUser] = None

    model_config = ConfigDict(from_attributes=True)


class FriendRequestUpdate(BaseModel):
    status: FriendRequestStatus