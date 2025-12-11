import uuid
from pydantic import BaseModel
from datetime import datetime


class MessageDeletionBase(BaseModel):
    message_id: uuid.UUID
    user_id: uuid.UUID


class MessageDeletionRead(MessageDeletionBase):
    id: uuid.UUID
    deleted_at: datetime

    model_config = {
        "from_attributes": True
    }
