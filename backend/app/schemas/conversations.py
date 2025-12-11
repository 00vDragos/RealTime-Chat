import uuid
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class ConversationBase(BaseModel):
    type: str


class ConversationCreate(BaseModel):
    participants: Optional[List[uuid.UUID]] = None


class ConversationRead(ConversationBase):
    id: uuid.UUID
    created_at: Optional[datetime] = None
    last_message_id: Optional[uuid.UUID] = None
    last_message_preview: Optional[str] = None
    last_message_created_at: Optional[datetime] = None

    class Config:
        orm_mode = True




class ConversationSummary(BaseModel):
    id: uuid.UUID
    friend_id: uuid.UUID = Field(alias="friendId")
    friend_name: str = Field(alias="friendName")
    friend_avatar: str | None = Field(alias="friendAvatar", default=None)
    last_message: str | None = Field(alias="lastMessage")
    last_message_time: datetime | None = Field(alias="lastMessageTime")
    unread_count: int = Field(alias="unreadCount")
    participant_ids: Optional[List[uuid.UUID]] = Field(default=None, alias="participantIds")
    participant_names: Optional[List[str]] = Field(default=None, alias="participantNames")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)