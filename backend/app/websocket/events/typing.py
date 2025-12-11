import uuid
from typing import Dict, Any, List

from app.websocket.manager import manager
from app.db.session import AsyncSessionLocal
from app.db.repositories.conversation_participants.get_all_participants import get_participants
from app.services.conversation_participants.get_participant_name import get_participant_name_service

async def handle_typing(user_id: str, data: Dict[str, Any], event_type: str) -> None:
    try:
        conversation_id_str = data.get("conversation_id")
        if not conversation_id_str:
            return

        async with AsyncSessionLocal() as db:
            participants = await get_participants(db, uuid.UUID(conversation_id_str))
            sender_name = await get_participant_name_service(db, uuid.UUID(user_id))

        participant_ids: List[str] = [str(p.user_id) for p in participants]

        await manager.broadcast(
            participant_ids,
            {
                "event": event_type,
                "conversation_id": conversation_id_str,
                "user_id": user_id,
                "sender_name": sender_name,
            },
        )
    except Exception:
        return

