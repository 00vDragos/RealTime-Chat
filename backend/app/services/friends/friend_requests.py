from typing import Optional
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.models.users import User
from app.models.friend_requests import FriendRequest
from app.models.friendships import Friendship


class FriendRequestService:
    @staticmethod
    async def find_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def _existing_friendship(db: AsyncSession, a: UUID, b: UUID) -> Optional[Friendship]:
        stmt = select(Friendship).where(
            or_(
                (Friendship.user_a_id == a) & (Friendship.user_b_id == b),
                (Friendship.user_a_id == b) & (Friendship.user_b_id == a),
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def _existing_friend_request(db: AsyncSession, a: UUID, b: UUID) -> Optional[FriendRequest]:
        stmt = select(FriendRequest).where(
            or_(
                (FriendRequest.from_user_id == a) & (FriendRequest.to_user_id == b),
                (FriendRequest.from_user_id == b) & (FriendRequest.to_user_id == a),
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    @staticmethod
    async def send_request(db: AsyncSession, from_user_id: UUID, to_email: str) -> FriendRequest:
        # find recipient
        to_user = await FriendRequestService.find_user_by_email(db, to_email)
        if not to_user:
            raise HTTPException(status_code=404, detail="User with this email not found")

        # prevent sending to self
        if str(to_user.id) == str(from_user_id):
            raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")

        # prevent if already friends
        if await FriendRequestService._existing_friendship(db, from_user_id, to_user.id):
            raise HTTPException(status_code=409, detail="Users are already friends")

        # prevent duplicate request (either direction)
        existing = await FriendRequestService._existing_friend_request(db, from_user_id, to_user.id)
        if existing:
            raise HTTPException(status_code=409, detail="Friend request already exists")

        # create friend request
        fr = FriendRequest(from_user_id=from_user_id, to_user_id=to_user.id, status="pending")
        db.add(fr)
        await db.flush()
        await db.refresh(fr)
        # commit here or let caller commit depending on your transaction pattern
        await db.commit()
        return fr