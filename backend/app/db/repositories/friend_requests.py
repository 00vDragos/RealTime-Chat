from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.friend_requests import FriendRequest


class FriendRequestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, from_user_id: UUID, to_user_id: UUID, status: str = "pending") -> FriendRequest:
        fr = FriendRequest(from_user_id=from_user_id, to_user_id=to_user_id, status=status)
        self.db.add(fr)
        await self.db.flush()
        await self.db.refresh(fr)
        return fr

    async def get_by_pair(self, from_user_id: UUID, to_user_id: UUID) -> Optional[FriendRequest]:
        stmt = select(FriendRequest).where(
            FriendRequest.from_user_id == from_user_id,
            FriendRequest.to_user_id == to_user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_for_user(self, user_id: UUID) -> List[FriendRequest]:
        stmt = select(FriendRequest).where(
            or_(FriendRequest.to_user_id == user_id, FriendRequest.from_user_id == user_id)
        ).order_by(FriendRequest.created_at.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, fr_id: UUID) -> Optional[FriendRequest]:
        stmt = select(FriendRequest).where(FriendRequest.id == fr_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_status(self, fr_id: UUID, new_status: str) -> Optional[FriendRequest]:
        fr = await self.get_by_id(fr_id)
        if not fr:
            return None
        fr.status = new_status
        await self.db.flush()
        await self.db.refresh(fr)
        return fr

    async def delete(self, fr_id: UUID) -> None:
        stmt = delete(FriendRequest).where(FriendRequest.id == fr_id)
        await self.db.execute(stmt)
        await self.db.flush()