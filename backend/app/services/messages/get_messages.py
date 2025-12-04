import uuid
from typing import Sequence

from app.models.messages import Message
from app.db.repositories.messages.get_messages import get_messages


async def get_messages_service(db, conversation_id: uuid.UUID, limit: int = 50, offset: int = 0) -> Sequence[Message] | None:
    try:
        msgs = await get_messages(db, conversation_id, limit, offset)
        msgs = [m for m in msgs if not m.deleted_for_everyone]

        return msgs

    except:
        return None