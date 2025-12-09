import uuid
#from datetime import datetime
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


from app.db.repositories.messages.create_message import create_message
from app.models.messages import Message
from app.models.conversations import Conversations

async def send_message_service(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        body: str
) -> Message | None:
    try:
        # Cream mesajul
        msg = await create_message(db, conversation_id, user_id, body)
        if not msg:
            return None

        #Pregatim update-ul conversației
        stmt = (
            update(Conversations)
            .where(Conversations.id == conversation_id)
            .values(
                last_message_id=msg.id,
                last_message_preview=body[:100],  # max 100 chars
                last_message_created_at=msg.created_at,
            )
        )

        await db.execute(stmt)

        #Salvam modificările
        await db.commit()

        return msg

    except Exception as e:
        await db.rollback()
        print("Error in send_message_service:", e)
        return None