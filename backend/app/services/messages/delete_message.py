import uuid
from app.db.repositories.messages.delete_message import delete_message
from app.services.messages.get_messages import get_messages_service
from app.models.message_deletions import MessageDeletion


async def delete_message_service(
    db,
    message_id: uuid.UUID,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID
) -> MessageDeletion | None:
    try:
        msgs = await get_messages_service(db, conversation_id)
        msg = next((m for m in msgs if m.id == message_id), None)

        if msg is None:
            raise ValueError("Message not found")

        if msg.sender_id != user_id:
            raise PermissionError("Cannot delete message sent by another user")

        deletion = await delete_message(db, message_id, user_id)
        return deletion

    except Exception:
        return None