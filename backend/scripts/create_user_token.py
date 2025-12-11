import sys
from pathlib import Path
import asyncio
import argparse

from app.core.security import create_access_token
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models.users import User
from datetime import timedelta

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'backend'))


async def create_token_for_email(email: str, minutes: int = 60):
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.email == email))
        user = res.scalars().first()
        if not user:
            print(f"User with email {email} not found")
            return
        data = {"id": str(user.id), "email": user.email}
        token = create_access_token(data=data, expires_delta=timedelta(minutes=minutes))
        print(token)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('email', nargs='?', default='alice@example.com')
    parser.add_argument('--minutes', type=int, default=60)
    args = parser.parse_args()
    asyncio.run(create_token_for_email(args.email, args.minutes))
