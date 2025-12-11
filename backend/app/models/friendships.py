import uuid
from sqlalchemy import Column, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.session import Base
from sqlalchemy import ForeignKey

class Friendship(Base):
    __tablename__ = "friendships"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_a_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user_b_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(TIMESTAMP, nullable=True)

    __table_args__ = (
        Index("uq_friendships_pair", "user_a_id", "user_b_id", unique=True),
    )