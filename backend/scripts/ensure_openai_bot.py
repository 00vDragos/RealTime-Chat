import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.users import User
from app.services.ai.openai_bot import ensure_openai_bot_user, ensure_user_has_openai_friendship
from app.core.config import settings


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await ensure_openai_bot_user(db)
        stmt = select(User.id).where(User.id != settings.OPENAI_BOT_USER_ID)
        result = await db.execute(stmt)
        users = result.scalars().all()
        for user_id in users:
            await ensure_user_has_openai_friendship(db, user_id)


if __name__ == "__main__":
    asyncio.run(main())
