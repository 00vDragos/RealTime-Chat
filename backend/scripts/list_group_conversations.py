import sys
from pathlib import Path
import asyncio

from app.db.session import AsyncSessionLocal
from app.db.repositories.conversation_repo import ConversationRepository
from app.models.conversations import Conversations
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'backend'))




async def list_group_conversations():
    async with AsyncSessionLocal() as db:
        repo = ConversationRepository(db)
        stmt = select(Conversations)
        convs = (await db.execute(stmt)).scalars().all()

        groups = []
        for conv in convs:
            pids = await repo.get_participant_ids(conv.id)
            if len(pids) > 2:
                names = []
                for pid in pids:
                    user = await repo.get_user(pid)
                    names.append(user.display_name if user else "Unknown")
                groups.append({
                    "id": str(conv.id),
                    "participantIds": [str(p) for p in pids],
                    "participantNames": names,
                })

        for g in groups:
            print(g)

        print(f"Total group conversations: {len(groups)}")


if __name__ == '__main__':
    asyncio.run(list_group_conversations())
