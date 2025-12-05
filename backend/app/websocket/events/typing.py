import uuid
from typing import Dict, Any, List

from app.websocket.manager import manager
from app.db.session import AsyncSessionLocal
from app.db.repositories.conversation_participants.get_all_participants import get_participants

async def handle_typing_start(user_id: str, data: Dict[str, Any]) -> None:
    try:
        conversation_id_str = data.get("conversation_id")
        if not conversation_id_str:
            return

        async with AsyncSessionLocal() as db:
            participants = await get_participants(db, uuid.UUID(conversation_id_str))

        participant_ids: List[str] = [str(p.user_id) for p in participants]

        await manager.broadcast(
            participant_ids,
            {
                "event": "typing_start",
                "conversation_id": conversation_id_str,
                "user_id": user_id,
            },
        )
    except Exception:
        return


async def handle_typing_stop(user_id: str, data: Dict[str, Any]) -> None:
    try:
        conversation_id_str = data.get("conversation_id")
        if not conversation_id_str:
            return

        async with AsyncSessionLocal() as db:
            participants = await get_participants(db, uuid.UUID(conversation_id_str))

        participant_ids: List[str] = [str(p.user_id) for p in participants]

        await manager.broadcast(
            participant_ids,
            {
                "event": "typing_stop",
                "conversation_id": conversation_id_str,
                "user_id": user_id,
            },
        )

    except Exception:
        return
