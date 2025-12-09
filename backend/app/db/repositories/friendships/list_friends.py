import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.friendships import Friendship
from app.models.users import users as User

async def list_friends_repo(db: AsyncSession, user_id: uuid.UUID) -> List[User]:
    # Find friendships where the user is either side, then return the other user
    stmt = select(User).where(
        or_(User.id.in_(select(Friendship.user_b_id).where(Friendship.user_a_id == user_id)),
            User.id.in_(select(Friendship.user_a_id).where(Friendship.user_b_id == user_id)))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
