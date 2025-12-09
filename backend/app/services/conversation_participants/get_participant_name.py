from app.db.repositories.conversation_participants.get_participant_name import get_participant_name

async def get_participant_name_service(db, user_id) -> str:
    try:
        return await get_participant_name(db, user_id)
    except Exception:
        return ""