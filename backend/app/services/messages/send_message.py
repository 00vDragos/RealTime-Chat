import uuid
from app.db.repositories.messages.create_message import create_message
from app.models.messages import Message


async def send_message_service(
    db,
    conversation_id: uuid.UUID,
    user_id: uuid.UUID,
    body: str
) -> Message | None:
    try:
        msg = await create_message(db, conversation_id, user_id, body)
        return msg

    except Exception:
        return None