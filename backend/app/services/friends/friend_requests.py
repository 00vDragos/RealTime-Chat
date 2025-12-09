from typing import Optional
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from typing import List

from sqlalchemy import delete

from app.models.users import users
from app.models.friend_requests import FriendRequest
from app.models.friendships import Friendship
from app.websocket.manager import manager


class FriendRequestService:
    async def find_user_by_email(db: AsyncSession, email: str) -> Optional[users]:
        stmt = select(users).where(users.email == email)
        res = await db.execute(stmt)
        return res.scalars().first()

    async def _existing_friendship(db: AsyncSession, a: UUID, b: UUID) -> Optional[Friendship]:
        stmt = select(Friendship).where(
            or_(
                (Friendship.user_a_id == a) & (Friendship.user_b_id == b),
                (Friendship.user_a_id == b) & (Friendship.user_b_id == a),
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first()

    async def _existing_friend_request(db: AsyncSession, a: UUID, b: UUID) -> Optional[FriendRequest]:
        stmt = select(FriendRequest).where(
            or_(
                (FriendRequest.from_user_id == a) & (FriendRequest.to_user_id == b),
                (FriendRequest.from_user_id == b) & (FriendRequest.to_user_id == a),
            )
        )
        res = await db.execute(stmt)
        return res.scalars().first()

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

    async def list_requests(db: AsyncSession, user_id: UUID, direction: Optional[str] = None) -> List[FriendRequest]:
        stmt = select(FriendRequest)
        if direction == "in":
            stmt = stmt.where(FriendRequest.to_user_id == user_id)
        elif direction == "out":
            stmt = stmt.where(FriendRequest.from_user_id == user_id)
        else:
            stmt = stmt.where(or_(FriendRequest.to_user_id == user_id, FriendRequest.from_user_id == user_id))

        stmt = stmt.order_by(FriendRequest.created_at.desc())
        res = await db.execute(stmt)
        return res.scalars().all()

    async def cancel_request(db: AsyncSession, user_id: UUID, request_id: UUID) -> None:
        # Only sender can cancel
        stmt = select(FriendRequest).where(FriendRequest.id == request_id)
        res = await db.execute(stmt)
        fr = res.scalars().first()
        if not fr:
            raise HTTPException(status_code=404, detail="Friend request not found")
        if str(fr.from_user_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Only sender can cancel the request")
        del_stmt = delete(FriendRequest).where(FriendRequest.id == request_id)
        await db.execute(del_stmt)
        await db.commit()

    async def list_friends(db: AsyncSession, user_id: UUID) -> List[users]:
        # find friendships where user is user_a or user_b and return the other user's info
        stmt = select(Friendship).where(or_(Friendship.user_a_id == user_id, Friendship.user_b_id == user_id))
        res = await db.execute(stmt)
        frs = res.scalars().all()
        other_ids = []
        for f in frs:
            other_ids.append(f.user_b_id if f.user_a_id == user_id else f.user_a_id)

        if not other_ids:
            return []

        # load users
        stmt2 = select(users).where(users.id.in_(other_ids))
        res2 = await db.execute(stmt2)
        return res2.scalars().all()

    async def remove_friend(db: AsyncSession, user_id: UUID, friend_id: UUID) -> None:
        # delete friendship in either direction
        stmt = delete(Friendship).where(
            or_(
                (Friendship.user_a_id == user_id) & (Friendship.user_b_id == friend_id),
                (Friendship.user_a_id == friend_id) & (Friendship.user_b_id == user_id),
            )
        )
        await db.execute(stmt)
        await db.commit()

    async def respond_request(db: AsyncSession, user_id: UUID, request_id: UUID, status: str) -> FriendRequest:
        # load friend request
        stmt = select(FriendRequest).where(FriendRequest.id == request_id)
        res = await db.execute(stmt)
        fr = res.scalars().first()
        if not fr:
            raise HTTPException(status_code=404, detail="Friend request not found")

        # only recipient can respond
        if str(fr.to_user_id) != str(user_id):
            raise HTTPException(status_code=403, detail="Only recipient can respond to this request")

        if status not in ("accepted", "declined"):
            raise HTTPException(status_code=400, detail="Invalid status")

        fr.status = status

        if status == "accepted":
            # create friendship (ensure ordering)
            a = fr.from_user_id
            b = fr.to_user_id
            # avoid duplicates
            existing = await FriendRequestService._existing_friendship(db, a, b)
            if not existing:
                # order deterministically so unique index matches
                user_a, user_b = (a, b) if str(a) < str(b) else (b, a)
                friendship = Friendship(user_a_id=user_a, user_b_id=user_b)
                db.add(friendship)

        await db.flush()
        await db.refresh(fr)
        await db.commit()

        # optional notification broadcast to both users
        try:
            participant_ids = [str(fr.from_user_id), str(fr.to_user_id)]
            await manager.broadcast(participant_ids, {"event": "friend_request_responded", "request_id": str(fr.id), "status": fr.status})
        except Exception:
            # non-fatal if websocket fails
            pass

        return fr