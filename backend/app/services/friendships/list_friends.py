import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.friendships.list_friends import list_friends_repo
from app.models.users import User

async def list_friends_service(db: AsyncSession, user_id: uuid.UUID) -> List[User]:
    return await list_friends_repo(db, user_id)
