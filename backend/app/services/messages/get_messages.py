import uuid
from typing import Sequence

from app.models.messages import Message
from app.db.repositories.messages.get_messages import get_messages
from app.services.conversation_participants.get_participant_name import get_participant_name_service


async def get_messages_service(db, conversation_id: uuid.UUID, limit: int = 50, offset: int = 0) -> Sequence[Message] | None:
    try:
        msgs = await get_messages(db, conversation_id, limit, offset)
        for m in msgs:
            m.sender_name = await get_participant_name_service(db, m.sender_id)

        return msgs

    except Exception:
        return None