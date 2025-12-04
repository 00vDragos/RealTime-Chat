from app.db.repositories.conversation_participants.get_participant import get_participant


async def is_conversation_participant_service(db, conversation_id, user_id) -> bool:
    try:
        await get_participant(db, conversation_id, user_id)
        return True
    except:
        return False