import uuid
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class MessageBase(BaseModel):
    conversation_id: uuid.UUID
    sender_id: uuid.UUID
    body: str


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: uuid.UUID
    sender_name: Optional[str] = None
    created_at: datetime
    delivered_at: Optional[Dict[str, Any]] = None
    seen_at: Optional[Dict[str, Any]] = None
    edited_at: Optional[datetime] = None
    deleted_for_everyone: bool = False

    class Config:
        orm_mode = True
