import uuid
from sqlalchemy import Column, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey
from backend.app.db.session import Base


class MessageDeletion(Base):
    __tablename__ = "message_deletions"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(PG_UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    deleted_at = Column(TIMESTAMP, nullable=False)

    __table_args__ = (
        Index("uq_message_deletions_pair", "message_id", "user_id", unique=True),
    )
