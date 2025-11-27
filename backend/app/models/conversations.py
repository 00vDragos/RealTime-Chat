from sqlalchemy import Column, Integer, String
from app.db.session import Base


class Conversations(Base):
    __tablename__="conversations"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # e.g., 'private', 'group'
    created_at = Column(String, nullable=False)  # ISO formatted datetime string