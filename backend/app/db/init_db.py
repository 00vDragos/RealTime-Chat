from typing import Callable

from app.db.session import engine, Base

from app.models.users import users
from app.models.conversations import Conversations
from app.models.conversation_participants import ConversationsParticipants
from app.models.messages import Message

async def init_db(
    create_tables: bool = False,
    run_migrations: bool = False,
    alembic_callable: Callable | None = None,
) -> None:
    """Initialize the database on app startup.

    - `create_tables`: if True, run `Base.metadata.create_all()` (good for quick dev setup).
    - `run_migrations`: if True and `alembic_callable` provided, call it to run Alembic migrations.

    Note: Prefer migrations for production. `create_tables=True` is intended for development only.
    """
    if create_tables:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    if run_migrations and alembic_callable:
        # Caller can pass a function that runs alembic programmatically or via subprocess
        alembic_callable()
