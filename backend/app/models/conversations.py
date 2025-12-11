import uuid
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy import ForeignKey, Text
from sqlalchemy import TIMESTAMP as SQLTIMESTAMP

class Conversations(Base):
    __tablename__ = "conversations"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)  # 'direct'|'group'
    created_at = Column(TIMESTAMP, nullable=True)
    participants = relationship("ConversationsParticipants", back_populates="conversation", cascade="all, delete-orphan")
    title = Column(String(255), nullable=True)
    # Denormalized last message fields for fast UI
    last_message_id = Column(PG_UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True, index=True)
    last_message_preview = Column(Text, nullable=True)
    last_message_created_at = Column(SQLTIMESTAMP, nullable=True)