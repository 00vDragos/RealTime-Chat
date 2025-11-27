from sqlalchemy import Column, Integer, String
from app.db.session import Base

class FriendRequests(Base):
    __tablename__="friend_requests"
    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, nullable=False)
    to_user_id = Column(Integer, nullable=False)
    status = Column(String, nullable=False)  # e.g., 'pending', 'accepted', 'rejected'
    created_at = Column(String, nullable=False)  # ISO formatted datetime string
    updated_at = Column(String, nullable=False)  # ISO formatted datetime string