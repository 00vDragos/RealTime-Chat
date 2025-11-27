from sqlalchemy import Column, Integer, String
from app.db.session import Base

class FriendShips(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, nullable=False)
    user_b_id = Column(Integer, nullable=False)
    created_at = Column(String, nullable=False)  # ISO formatted datetime string