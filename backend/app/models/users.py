import uuid
from sqlalchemy import Column, String, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, unique=True, index=True)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    provider = Column(String, nullable=True)  # 'google'|'facebook'
    provider_sub = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)

    __table_args__ = (
        Index("idx_users_email", "email"),
    )

# Backwards compatibility: some modules import `users` (lowercase)
users = User