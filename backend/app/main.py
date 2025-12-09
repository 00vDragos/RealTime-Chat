# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db
from app.core.config import settings

# MESSAGE-RELATED ROUTES
from app.routes.messages.send_message import router as send_message_router
from app.routes.messages.edit_message import router as edit_message_router
from app.routes.messages.delete_message import router as delete_message_router
from app.routes.messages.get_messages import router as get_messages_router
from app.routes.messages.update_last_read import router as update_last_read_router
from app.routes.messages.conversations import router as conversations_router

# WEBSOCKET ROUTES
from app.websocket.router import router as websocket_router


app = FastAPI(title=settings.APP_NAME)

# CORS (allow frontend dev origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Message routes

app.include_router(send_message_router, tags=["messages"])
app.include_router(edit_message_router, tags=["messages"])
app.include_router(delete_message_router, tags=["messages"])
app.include_router(conversations_router, tags=["messages"])

# Conversations routes
app.include_router(get_messages_router, tags=["conversation_participants"])
app.include_router(update_last_read_router, tags=["conversation_participants"])

# Websocket routes
app.include_router(websocket_router, tags=["websocket"])



@app.on_event("startup")
async def on_startup():
    # In development we create tables for convenience. In production use Alembic migrations.
    if settings.DEBUG:
        await init_db(create_tables=True)



