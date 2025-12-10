import uuid
from sqlalchemy import Column, String, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from backend.app.db.session import Base
from sqlalchemy import ForeignKey

class FriendRequest(Base):
    __tablename__ = "friend_requests"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    to_user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False)  # use app Enum or DB enum: pending|accepted|declined|canceled
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)

    __table_args__ = (
        Index("uq_friend_requests_pair", "from_user_id", "to_user_id", unique=True),
    )