import uuid
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: Optional[str] = None
    provider_id: Optional[str] = None

      
class UserRead(UserBase):
    id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)