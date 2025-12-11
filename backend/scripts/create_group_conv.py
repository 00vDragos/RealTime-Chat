import sys
from pathlib import Path
import asyncio
import argparse

from app.db.session import AsyncSessionLocal
from app.db.repositories.conversation_repo import ConversationRepository
from app.services.conversation_service import ConversationService
from sqlalchemy import select
from app.models.users import User

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'backend'))


async def create_group_by_emails(emails: list[str]):
    async with AsyncSessionLocal() as db:
        # resolve emails to user ids
        users = []
        for email in emails:
            res = await db.execute(select(User).where(User.email == email))
            u = res.scalars().first()
            if not u:
                print(f"User not found: {email}")
                return
            users.append(u.id)

        # pick the first user as the requester for tokenless script convenience
        requester_id = users[0]
        repo = ConversationRepository(db)
        service = ConversationService(repo)
        summary = await service.create_conversation(requester_id, users)
        print(summary)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('emails', nargs='+', help='Emails of participants (include requester)')
    args = parser.parse_args()
    asyncio.run(create_group_by_emails(args.emails))
