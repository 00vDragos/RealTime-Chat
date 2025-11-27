import uuid
from sqlalchemy import Column, Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from app.db.session import Base
from sqlalchemy import ForeignKey

class Message(Base):
    __tablename__ = "messages"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(PG_UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    sender_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    delivered_at = Column(JSONB, nullable=True)  # per-recipient map
    seen_at = Column(JSONB, nullable=True)

    __table_args__ = (
        Index("idx_messages_conversation_created_at", "conversation_id", "created_at"),
    )