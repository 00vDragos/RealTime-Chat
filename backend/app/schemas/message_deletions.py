import uuid
from pydantic import BaseModel
from datetime import datetime


class MessageDeletionBase(BaseModel):
    message_id: uuid.UUID
    user_id: uuid.UUID


class MessageDeletionCreate(MessageDeletionBase):
    pass


class MessageDeletionRead(MessageDeletionBase):
    id: uuid.UUID
    deleted_at: datetime

    class Config:
        orm_mode = True
