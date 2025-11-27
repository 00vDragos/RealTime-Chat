# app/main.py
from fastapi import FastAPI

from app.db.init_db import init_db
from app.core.config import settings


app = FastAPI(title=settings.APP_NAME)


@app.on_event("startup")
async def on_startup():
    # In development we create tables for convenience. In production use Alembic migrations.
    if settings.DEBUG:
        await init_db(create_tables=True)


@app.get("/healthz")
async def health_check():
    """
    Endpoint de verificare a stării aplicației.
    Îl poți accesa la http://localhost:8000/healthz
    după ce rulezi containerul.
    """
    return {"status": "ok", "message": "Backend is healthy "}
