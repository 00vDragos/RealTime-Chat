# app/main.py
from app.db.init_db import init_db
from app.core.config import settings

from app.routes.messages.send_message import router as send_message_router
from app.routes.messages.edit_message import router as edit_message_router
from app.routes.messages.delete_message import router as delete_message_router
from app.routes.conversation_participants.get_messages import router as get_messages_router
from app.routes.conversation_participants.update_last_read import router as update_last_read_router
from app.websocket.router import router as websocket_router
from fastapi import FastAPI

app = FastAPI(title=settings.APP_NAME)

app.include_router(send_message_router, tags=["messages"])
app.include_router(edit_message_router, tags=["messages"])
app.include_router(delete_message_router, tags=["messages"])

app.include_router(get_messages_router, tags=["conversation_participants"])
app.include_router(update_last_read_router, tags=["conversation_participants"])

app.include_router(websocket_router, tags=["websocket"])

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
