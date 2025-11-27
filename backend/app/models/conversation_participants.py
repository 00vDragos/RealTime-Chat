import uuid
from sqlalchemy import Column, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class ConversationsParticipants(Base):
    __tablename__ = "conversation_participants"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # optional PK
    conversation_id = Column(PG_UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    joined_at = Column(TIMESTAMP, nullable=True)
    conversation = relationship("Conversations", back_populates="participants")