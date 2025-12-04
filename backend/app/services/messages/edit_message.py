import uuid
from app.db.repositories.messages.edit_message import edit_message
from app.services.messages.get_messages import get_messages
from app.models.messages import Message


async def edit_message_service(
    db,
    message_id: uuid.UUID,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    new_body: str
) -> Message | None:
    try:
        msgs = await get_messages(db, conversation_id)
        msg = next((m for m in msgs if m.id == message_id), None)

        if msg is None:
            raise ValueError("Message not found")

        if msg.sender_id != user_id:
            raise PermissionError("Cannot edit message sent by another user")

        updated = await edit_message(db, message_id, new_body)
        return updated

    except:
        return None
