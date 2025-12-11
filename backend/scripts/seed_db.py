import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

# -------------------------------------------------------------------
# App imports (config + models) — keep imports at top for ruff E402
# -------------------------------------------------------------------
from backend.app.core.config import settings
from backend.app.models.users import User
from backend.app.models.conversations import Conversations
from backend.app.models.conversation_participants import ConversationsParticipants
from backend.app.models.messages import Message
from backend.app.models.friend_requests import FriendRequest
from backend.app.models.friendships import Friendship
from backend.app.models.message_deletions import MessageDeletion
from backend.app.models.refresh_tokens import RefreshToken

# -------------------------------------------------------------------
# Ensure script can import when run from different working directories
# (adjust sys.path after imports to satisfy lint rule E402)
# -------------------------------------------------------------------
THIS_FILE = Path(__file__).resolve()
BACKEND_DIR = THIS_FILE.parents[1]        # .../RealTime-Chat/backend
PROJECT_ROOT = BACKEND_DIR.parent         # .../RealTime-Chat

for p in (PROJECT_ROOT, BACKEND_DIR):
    p_str = str(p)
    if p_str not in sys.path:
        sys.path.insert(0, p_str)

# -------------------------------------------------------------------
# Sync engine & SessionLocal (we derive a psycopg URL from asyncpg URL)
# -------------------------------------------------------------------
SYNC_DATABASE_URL = settings.database_url.replace("+asyncpg", "")
print(settings.database_url.replace("+asyncpg", ""))
engine = create_engine(SYNC_DATABASE_URL, echo=settings.DEBUG)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    # Users.created_at / updated_at are String columns in your model
    return now_utc().isoformat()


def create_users(db) -> Dict[str, User]:
    """Create a few demo users (id is UUID)."""

    # email is unique, so we can upsert-style by email
    existing = {u.email: u for u in db.query(User).all()}

    def get_or_create(email: str, display_name: str, provider: str, provider_sub: str) -> User:
        if email in existing:
            return existing[email]

        user = User(
            email=email,
            display_name=display_name,
            avatar_url=None,
            provider=provider,
            provider_sub=provider_sub,
            created_at=iso_now(),
            updated_at=iso_now(),
        )
        db.add(user)
        db.flush()  # populate user.id
        existing[email] = user
        return user

    alice = get_or_create("alice@example.com", "Alice", "local", "alice_local")
    bob = get_or_create("bob@example.com", "Bob", "local", "bob_local")
    charlie = get_or_create("charlie@example.com", "Charlie", "local", "charlie_local")
    dave = get_or_create("dave@example.com", "Dave", "local", "dave_local")

    return {
        "alice": alice,
        "bob": bob,
        "charlie": charlie,
        "dave": dave,
    }


def ensure_friendship(db, user_a_id, user_b_id) -> Friendship:
    """Create an undirected friendship pair if it doesn't exist yet."""
    pair = (
        db.query(Friendship)
        .filter(
            or_(
                (Friendship.user_a_id == user_a_id) & (Friendship.user_b_id == user_b_id),
                (Friendship.user_a_id == user_b_id) & (Friendship.user_b_id == user_a_id),
            )
        )
        .first()
    )
    if pair:
        return pair

    friendship = Friendship(
        user_a_id=user_a_id,
        user_b_id=user_b_id,
        created_at=now_utc(),
    )
    db.add(friendship)
    db.flush()
    return friendship


def get_or_create_conversation(db, conv_type: str, title: str) -> Conversations:
    """Create a conversation row; 'type' is 'direct' | 'group' by your model."""
    convo = (
        db.query(Conversations)
        .filter(
            Conversations.type == conv_type,
            Conversations.last_message_preview == title,  # simple marker
        )
        .first()
    )
    if convo:
        return convo

    convo = Conversations(
        type=conv_type,
        created_at=now_utc(),
        last_message_id=None,
        last_message_preview=title,          # reuse preview as a 'name'
        last_message_created_at=None,
    )
    db.add(convo)
    db.flush()
    return convo


def ensure_participant(db, conversation_id, user_id) -> ConversationsParticipants:
    cp = (
        db.query(ConversationsParticipants)
        .filter(
            ConversationsParticipants.conversation_id == conversation_id,
            ConversationsParticipants.user_id == user_id,
        )
        .first()
    )
    if cp:
        return cp

    cp = ConversationsParticipants(
        conversation_id=conversation_id,
        user_id=user_id,
        joined_at=now_utc() - timedelta(hours=1),
        last_read_message_id=None,
    )
    db.add(cp)
    db.flush()
    return cp


def seed_messages(
    db,
    conversation: Conversations,
    senders: List[User],
    base_texts: List[str],
) -> List[Message]:
    """Create a bunch of messages in a conversation."""
    already = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .first()
    )
    if already:
        # Don't duplicate messages if we already seeded this conversation
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
            .all()
        )

    base_time = now_utc() - timedelta(days=1)
    messages: List[Message] = []

    idx = 0
    for sender in senders:
        for text in base_texts:
            created_at = base_time + timedelta(minutes=idx * 5)
            msg = Message(
                conversation_id=conversation.id,
                sender_id=sender.id,
                body=f"{text} (by {sender.display_name})",
                created_at=created_at,
                delivered_at=None,
                seen_at=None,
                edited_at=None,
                deleted_for_everyone=False,
            )
            db.add(msg)
            messages.append(msg)
            idx += 1

    db.flush()
    return messages


def seed_friend_requests(db, users: Dict[str, User]) -> None:
    """Create a couple of friend requests with different statuses."""
    alice = users["alice"]
    charlie = users["charlie"]

    existing = (
        db.query(FriendRequest)
        .filter(
            FriendRequest.from_user_id == alice.id,
            FriendRequest.to_user_id == charlie.id,
        )
        .first()
    )
    if existing:
        return

    fr = FriendRequest(
        from_user_id=alice.id,
        to_user_id=charlie.id,
        status="pending",
        created_at=now_utc(),
        updated_at=None,
    )
    db.add(fr)


def seed_message_deletions(db, conversation: Conversations) -> None:
    """Mark one of the messages as deleted for a specific user."""
    msg = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at)
        .first()
    )
    if not msg:
        return

    # Pick some user who sent it
    user_id = msg.sender_id

    exists = (
        db.query(MessageDeletion)
        .filter(
            MessageDeletion.message_id == msg.id,
            MessageDeletion.user_id == user_id,
        )
        .first()
    )
    if exists:
        return

    deletion = MessageDeletion(
        message_id=msg.id,
        user_id=user_id,
        deleted_at=now_utc(),
    )
    db.add(deletion)


def seed_refresh_tokens(db, users: Dict[str, User]) -> None:
    """Create dummy refresh tokens for each user."""
    for name, user in users.items():
        existing = (
            db.query(RefreshToken)
            .filter(RefreshToken.user_id == user.id)
            .first()
        )
        if existing:
            continue

        token = RefreshToken(
            user_id=user.id,
            token_hash=f"hash_for_{name}",  # in real life you'd hash a random token
            expires_at=now_utc() + timedelta(days=30),
            revoked_at=None,
        )
        db.add(token)


def update_conversation_last_message(db, conversation: Conversations) -> None:
    """Update denormalized last_message_* fields on Conversations."""
    last_msg = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .first()
    )
    if not last_msg:
        return

    conversation.last_message_id = last_msg.id
    conversation.last_message_preview = last_msg.body[:200]
    conversation.last_message_created_at = last_msg.created_at


# -------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------
def main() -> None:
    db = SessionLocal()
    try:
        # 1) Users
        users = create_users(db)
        db.commit()  # commit users so we have stable UUIDs

        # 2) Friendships (undirected)
        ensure_friendship(db, users["alice"].id, users["bob"].id)
        ensure_friendship(db, users["alice"].id, users["charlie"].id)
        ensure_friendship(db, users["bob"].id, users["dave"].id)
        db.commit()

        # 3) Conversations
        general = get_or_create_conversation(db, conv_type="group",  title="General Chat")
        random = get_or_create_conversation(db, conv_type="group",  title="Random")
        dm_ab = get_or_create_conversation(db, conv_type="direct", title="Alice & Bob DM")
        db.commit()

        # 4) Participants
        for u in (users["alice"], users["bob"], users["charlie"]):
            ensure_participant(db, general.id, u.id)

        for u in (users["alice"], users["bob"]):
            ensure_participant(db, random.id, u.id)

        for u in (users["alice"], users["bob"]):
            ensure_participant(db, dm_ab.id, u.id)

        db.commit()

        # 5) Messages
        seed_messages(
            db,
            general,
            [users["alice"], users["bob"], users["charlie"]],
            [
                "Hey everyone!",
                "This is the general chat.",
                "We use this for most discussions.",
                "Remember to stay hydrated.",
            ],
        )

        seed_messages(
            db,
            random,
            [users["alice"], users["bob"]],
            [
                "Random memes go here.",
                "Did you see the latest framework?",
                "I broke the build again…",
            ],
        )

        seed_messages(
            db,
            dm_ab,
            [users["alice"], users["bob"]],
            [
                "Hey, this is our private DM.",
                "We can test typing indicators here.",
            ],
        )

        # Update last_message_* fields
        update_conversation_last_message(db, general)
        update_conversation_last_message(db, random)
        update_conversation_last_message(db, dm_ab)

        # 6) Friend requests
        seed_friend_requests(db, users)

        # 7) Message deletions
        seed_message_deletions(db, random)

        # 8) Refresh tokens
        seed_refresh_tokens(db, users)

        db.commit()
        print("✅ Seed complete: users, friendships, conversations, participants, messages, friend_requests, deletions, refresh_tokens.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
