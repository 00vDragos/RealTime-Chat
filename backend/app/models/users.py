from sqlalchemy import Column, Integer, String
from app.db.session import Base

class users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    display_name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    provider = Column(String, nullable=False)  # e.g., 'google', 'facebook'
    provider_id = Column(String, unique=True, nullable=False)  # ID from the OAuth provider
    created_at = Column(String, nullable=False)  # ISO formatted datetime string
    updated_at = Column(String, nullable=False)  # ISO formatted datetime string