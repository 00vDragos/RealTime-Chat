import uuid
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class Conversations(Base):
    __tablename__ = "conversations"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)  # 'direct'|'group'
    created_at = Column(TIMESTAMP, nullable=True)
    participants = relationship("ConversationsParticipants", back_populates="conversation", cascade="all, delete-orphan")