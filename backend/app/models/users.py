import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime, func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"


    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    provider = Column(String, nullable=True)  # e.g., 'google', 'facebook'
    provider_sub = Column(String, unique=True, nullable=True)  # ID from the OAuth provider
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # ISO formatted datetime string
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)  # ISO formatted datetime string