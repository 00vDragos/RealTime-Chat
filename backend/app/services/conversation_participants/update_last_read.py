import uuid
from app.db.repositories.conversation_participants.update_last_read import update_last_read
from app.models.conversation_participants import ConversationsParticipants


async def update_last_read_service(
    db,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    message_id: uuid.UUID
) -> ConversationsParticipants | None:
    try:
        updated = await update_last_read(db, conversation_id, user_id, message_id)
        return updated

    except Exception:
        return None