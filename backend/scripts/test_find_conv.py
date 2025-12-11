import asyncio
from app.db.session import AsyncSessionLocal
from app.db.repositories.conversation_repo import ConversationRepository
import uuid


async def run():
    ids = [
        uuid.UUID('6a0bc187-2f37-44c2-8adb-747783188f8c'),
        uuid.UUID('c4ba3f58-9da0-4a84-bb46-1fd51ed530af'),
        uuid.UUID('ec20442f-8df4-470f-8897-5b1a03c65e5a'),
    ]
    async with AsyncSessionLocal() as db:
        repo = ConversationRepository(db)
        conv = await repo.find_conversation_by_participant_set(ids)
        print('found:', bool(conv))
        if conv:
            print('conv id:', conv.id)

if __name__ == '__main__':
    asyncio.run(run())
