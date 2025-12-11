from fastapi import APIRouter, Depends, HTTPException
import uuid

from app.services.conversation_participants.is_participant import is_conversation_participant_service
from app.websocket.manager import manager
from app.db.repositories.conversation_participants.get_all_participants import get_participants
from app.db.dependencies import get_current_user_id, get_current_conversation_id, get_db
from app.services.messages.send_message import send_message_service
from app.schemas.messages import MessageRead
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai.openai_bot import maybe_generate_openai_reply
from app.db.repositories.conversation_repo import ConversationRepository
from app.services.conversation_service import ConversationService

from app.services.conversation_participants.get_participant_name import get_participant_name_service

router = APIRouter()


@router.post("/conversations/{conversation_id}/messages", response_model=MessageRead)
async def send_message(
    body: str,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID = Depends(get_current_user_id),
    conversation_id: uuid.UUID = Depends(get_current_conversation_id)
):
    try:
        if not await is_conversation_participant_service(db, conversation_id, user_id):
            raise HTTPException(status_code=403, detail="Not a participant")

        # Check whether this conversation previously had a last message
        conv_repo = ConversationRepository(db)
        conv = await conv_repo.get_conversation_by_id(conversation_id)
        had_last_message = bool(getattr(conv, 'last_message_created_at', None))

        message = await send_message_service(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id,
            body=body)

        if not message:
            raise HTTPException(status_code=500, detail="Unable to send message")

        message.sender_name = await get_participant_name_service(db, message.sender_id)

        participants = await get_participants(db, conversation_id)
        participant_ids = [str(p.user_id) for p in participants]
        participant_uuids = [p.user_id for p in participants]

        # If this was the first message in the conversation, notify participants that
        # a conversation has effectively been created/activated so it appears in their list.
        if not had_last_message:
            try:
                summary = await ConversationService(conv_repo).create_conversation(user_id, participant_uuids)
                await manager.broadcast(
                    participant_ids,
                    {
                        "event": "conversation_created",
                        "conversation": summary,
                    }
                )
            except Exception:
                # Creating summary or broadcasting failing should not block sending the message
                pass

        await manager.broadcast(
            participant_ids,
            {
                "event": "new_message",
                "conversation_id": str(conversation_id),
                "message": {
                    "id": str(message.id),
                    "body": message.body,
                    "sender_id": str(message.sender_id),
                    "sender_name": message.sender_name,
                },
            }
        )

        try:
            bot_reply = await maybe_generate_openai_reply(
                db=db,
                conversation_id=conversation_id,
                participant_ids=participant_uuids,
                sender_id=message.sender_id,
            )
            if bot_reply:
                bot_reply.sender_name = await get_participant_name_service(db, bot_reply.sender_id)
                await manager.broadcast(
                    participant_ids,
                    {
                        "event": "new_message",
                        "conversation_id": str(conversation_id),
                        "message": {
                            "id": str(bot_reply.id),
                            "body": bot_reply.body,
                            "sender_id": str(bot_reply.sender_id),
                            "sender_name": bot_reply.sender_name,
                        },
                    }
                )
        except Exception as exc:
            print("OpenAI bot reply failed", exc)

        return message

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")