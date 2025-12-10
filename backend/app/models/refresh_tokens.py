import uuid
from sqlalchemy import Column, TIMESTAMP, String, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from backend.app.db.session import Base
from sqlalchemy import ForeignKey

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token_hash = Column(String, nullable=False, unique=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    revoked_at = Column(TIMESTAMP(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_refresh_tokens_user_id", "user_id"),
    )