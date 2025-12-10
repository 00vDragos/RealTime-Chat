import asyncio
from logging.config import fileConfig
import os

from sqlalchemy.engine import Connection

from alembic import context

# Import your settings and models metadata
# Make sure PYTHONPATH allows 'app' import (when running locally set PYTHONPATH='backend')
from backend.app.core.config import settings
from backend.app.db.session import Base  # Base.metadata is target_metadata

# this loads the alembic.ini config
config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Alembic's autogenerate only sees tables that have been imported into SQLAlchemy's
# metadata at runtime. Import the app's model modules here to ensure they are registered.
try:
    import backend.app.models.users
    import backend.app.models.friend_requests
    import backend.app.models.friendships
    import backend.app.models.messages
    import backend.app.models.message_deletions
    import backend.app.models.conversations
    import backend.app.models.refresh_tokens
    import backend.app.models.conversation_participants
except Exception :
    pass

# Use DATABASE_URL from settings (or environment)
DATABASE_URL = os.getenv("DATABASE_URL", settings.database_url)

# Import your models

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(DATABASE_URL, future=True)

    async with connectable.connect() as conn:
        await conn.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online():
    """Run migrations in 'online' mode (async)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
