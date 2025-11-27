import uuid
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConversationBase(BaseModel):
    type: str


class ConversationCreate(ConversationBase):
    participants: Optional[List[uuid.UUID]] = None


class ConversationRead(ConversationBase):
    id: uuid.UUID
    created_at: Optional[datetime] = None
    last_message_id: Optional[uuid.UUID] = None
    last_message_preview: Optional[str] = None
    last_message_created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
