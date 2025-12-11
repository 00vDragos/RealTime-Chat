import uuid
from datetime import datetime, timezone
from typing import List

from sqlalchemy import select, update

from app.db.session import AsyncSessionLocal
from app.models.conversation_participants import ConversationsParticipants
from app.models.users import User
from app.websocket.manager import manager


async def _get_related_user_ids(user_uuid: uuid.UUID) -> List[str]:
    async with AsyncSessionLocal() as db:
        conv_stmt = select(ConversationsParticipants.conversation_id).where(
            ConversationsParticipants.user_id == user_uuid
        )
        conv_ids = [row for row in (await db.execute(conv_stmt)).scalars().all()]
        if not conv_ids:
            return []

        participants_stmt = select(ConversationsParticipants.user_id).where(
            ConversationsParticipants.conversation_id.in_(conv_ids)
        )
        participant_ids = set((await db.execute(participants_stmt)).scalars().all())
        participant_ids.discard(user_uuid)
        return [str(pid) for pid in participant_ids]


async def handle_presence_change(user_id: str, is_online: bool) -> None:
    """Broadcast presence info to all conversation participants."""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        return

    last_seen_iso: str | None = None
    if not is_online:
        now = datetime.now(timezone.utc)
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(User).where(User.id == user_uuid).values(last_seen=now)
            )
            await db.commit()
        last_seen_iso = now.isoformat()

    related_user_ids = await _get_related_user_ids(user_uuid)
    if not related_user_ids:
        return

    await manager.broadcast(
        related_user_ids,
        {
            "event": "presence_update",
            "user_id": user_id,
            "is_online": is_online,
            "last_seen": last_seen_iso,
        },
    )
