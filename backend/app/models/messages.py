import uuid
from typing import ClassVar

from sqlalchemy import Column, Text, TIMESTAMP, Index, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from backend.app.db.session import Base
from sqlalchemy import ForeignKey

class Message(Base):
    __tablename__ = "messages"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(PG_UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    sender_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    sender_name: ClassVar[str | None] = None
    body = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    delivered_at = Column(JSONB, nullable=True)  # per-recipient map
    seen_at = Column(JSONB, nullable=True)
    edited_at = Column(TIMESTAMP, nullable=True)
    # mark that message was deleted for everyone
    deleted_for_everyone = Column(Boolean, nullable=False, default=False, server_default="false")

    __table_args__ = (
        Index("idx_messages_conversation_created_at", "conversation_id", "created_at"),
    )