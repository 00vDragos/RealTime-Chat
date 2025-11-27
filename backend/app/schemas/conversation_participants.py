import uuid
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConversationParticipantBase(BaseModel):
    conversation_id: uuid.UUID
    user_id: uuid.UUID

class ConversationParticipantRead(ConversationParticipantBase):
    id: uuid.UUID
    joined_at: Optional[datetime] = None

    class Config:
        orm_mode = True
