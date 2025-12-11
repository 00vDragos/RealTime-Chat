import uuid
from typing import Dict, List

from backend.app.websocket.manager import manager
from backend.app.db.session import AsyncSessionLocal
from backend.app.db.repositories.conversation_participants.get_all_participants import get_participants
from backend.app.schemas.messages import MessageRead

async def handle_reaction(
        conversation_id: uuid.UUID,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
        reactions: Dict[str, List[str]],
        event_type: str) -> None:
        
        try:
            async with AsyncSessionLocal() as db:
                
                participants = await get_participants(db, conversation_id)
                participant_ids: List[str] = [str(p.user_id) for p in participants]
                
                await manager.broadcast(
                    participant_ids,
                    {
                        "event": "message_reaction_updated",
                        "conversation_id": str(conversation_id),
                        "message_id": str(message_id),
                        "user_id": str(user_id),
                        "reactions": reactions, 
                        "action": event_type
                 },
                )
        except Exception as e:
            print(f"Error broadcasting reaction update: {e}")
            return
            

