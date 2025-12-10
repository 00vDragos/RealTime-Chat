import asyncio
from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from app.models.users import User
from app.services.friends.friend_requests import FriendRequestService


async def ensure_user(db, email: str):
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if user:
        return user

    # create minimal user (provider_id required)
    u = User(email=email, provider_id=email)
    db.add(u)
    await db.flush()
    await db.refresh(u)
    await db.commit()
    return u


async def main():
    async with AsyncSessionLocal() as db:
        # pick two test emails
        alice_email = "alice.test@example.com"
        bob_email = "bob.test@example.com"

        alice = await ensure_user(db, alice_email)
        bob = await ensure_user(db, bob_email)

        print("Users:")
        print(f" Alice: {alice.id} {alice.email}")
        print(f" Bob:   {bob.id} {bob.email}")

        # Send friend request from Alice to Bob
        print("Sending friend request from Alice to Bob...")
        fr = await FriendRequestService.send_request(db, from_user_id=alice.id, to_email=bob.email)
        print("Created FriendRequest:", fr.id, fr.status, fr.from_user_id, fr.to_user_id)

        # List Bob's incoming requests
        incoming = await FriendRequestService.list_requests(db, user_id=bob.id, direction="in")
        print("Bob incoming requests:", [(str(r.id), r.status) for r in incoming])

        # Bob accepts the request
        print("Bob accepts the request...")
        updated = await FriendRequestService.respond_request(db, user_id=bob.id, request_id=fr.id, status="accepted")
        print("Request status after accept:", updated.id, updated.status)

        # List friends for Alice
        friends_of_alice = await FriendRequestService.list_friends(db, user_id=alice.id)
        print("Alice friends:", [(str(u.id), u.email) for u in friends_of_alice])


if __name__ == "__main__":
    asyncio.run(main())
