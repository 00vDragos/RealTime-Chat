import os
import sys
from pathlib import Path
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

# Ensure backend package is on sys.path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'backend'))

# Force tests to use in-memory SQLite and disable dev startup DB init
# Prefer local Postgres from docker-compose for full dialect compatibility
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://chat:chatpwd@localhost:5432/chat_db")
os.environ.setdefault("DEBUG", "0")

from backend.app.main import app  # noqa: E402
from backend.app.db.dependencies import get_db  # noqa: E402
from backend.app.db.session import Base, engine  # noqa: E402


# Use pytest anyio/asyncio auto mode; no custom event loop fixture needed


@pytest.fixture(scope="session")
def api_base():
    # Using app mounting without proxy; avoid /api prefix in paths
    return os.environ.get("API_BASE", "http://localhost:8000")


@pytest.fixture(scope="session")
def async_session_factory(setup_database):
    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest.fixture(autouse=True, scope="session")
def override_get_db_session(async_session_factory):
    async def _get_db_override():
        async with async_session_factory() as session:
            yield session
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def client():
    # In-app client; DB override is applied session-wide
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# Force anyio to use asyncio backend only to avoid trio dependency
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# Removed legacy login_token fixture in favor of ensure_test_users


@pytest.fixture(scope="session")
def test_users():
    return [
        {"email": "ttt@test.com", "password": "parolatare1!", "display_name": "TTT"},
        {"email": "yyy@test.com", "password": "parolatare1!", "display_name": "YYY"},
        {"email": "uuu@test.com", "password": "parolatare1!", "display_name": "UUU"},
        {"email": "iii@test.com", "password": "parolatare1!", "display_name": "III"},
    ]


@pytest.fixture
async def ensure_test_users(client, test_users):
    created = []
    for user in test_users:
        # Try login first; if unauthorized, register then login
        resp_login = await client.post("/api/auth/login", json={
            "email": user["email"],
            "password": user["password"],
        })
        if resp_login.status_code == 200:
            created.append({"email": user["email"], "token": resp_login.json()["access_token"]})
            continue
        # Register
        resp_reg = await client.post("/api/auth/register", json={
            "email": user["email"],
            "password": user["password"],
            "display_name": user["display_name"],
        })
        assert resp_reg.status_code in (200, 201), resp_reg.text
        # Login to confirm
        resp_login2 = await client.post("/api/auth/login", json={
            "email": user["email"],
            "password": user["password"],
        })
        assert resp_login2.status_code == 200, resp_login2.text
        created.append({"email": user["email"], "token": resp_login2.json()["access_token"]})

    return created


@pytest.fixture(scope="session")
async def setup_database():
    # Ensure all tables exist on the same engine the app uses
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Remove function-scoped db_session; using factory + override instead


# Override app dependency to use the test DB session
# Removed global autouse override; client fixture applies override to ensure ordering
