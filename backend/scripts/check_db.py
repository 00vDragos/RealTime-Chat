import asyncio
import sys

sys.path.insert(0, "backend")

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.core.config import settings


async def main():
    print("Trying:", settings.database_url)
    engine = create_async_engine(settings.database_url, future=True)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("SELECT 1 ->", result.scalar_one())
    except Exception as exc:
        print("Connection failed:", type(exc).__name__, exc)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
