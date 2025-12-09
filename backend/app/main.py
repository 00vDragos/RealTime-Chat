# app/main.py
from fastapi import FastAPI

from app.db.init_db import init_db
from app.core.config import settings

# MESSAGE-RELATED ROUTES
from app.routes.messages.send_message import router as send_message_router
from app.routes.messages.edit_message import router as edit_message_router
from app.routes.messages.delete_message import router as delete_message_router
from app.routes.messages.get_messages import router as get_messages_router
from app.routes.messages.update_last_read import router as update_last_read_router
from app.routes.messages.conversations import router as conversations_router
from app.routes.friends.friends_requests import router as send_friend_request_router
from app.routes.friends.list_requests import router as list_friend_requests_router
from app.routes.friends.cancel_request import router as cancel_friend_request_router
from app.routes.friends.list_friends import router as list_friends_router
from app.routes.friends.remove_friend import router as remove_friend_router

# WEBSOCKET ROUTES
from app.websocket.router import router as websocket_router


app = FastAPI(title=settings.APP_NAME)

# Message routes

app.include_router(send_message_router, tags=["messages"])
app.include_router(edit_message_router, tags=["messages"])
app.include_router(delete_message_router, tags=["messages"])
app.include_router(conversations_router, tags=["messages"])

# Conversations routes
app.include_router(get_messages_router, tags=["conversation_participants"])
app.include_router(update_last_read_router, tags=["conversation_participants"])
app.include_router(send_friend_request_router, tags=["friends"])
app.include_router(list_friend_requests_router, tags=["friends"])
app.include_router(cancel_friend_request_router, tags=["friends"])
app.include_router(list_friends_router, tags=["friends"])
app.include_router(remove_friend_router, tags=["friends"])

# Websocket routes
app.include_router(websocket_router, tags=["websocket"])



@app.on_event("startup")
async def on_startup():
    # In development we create tables for convenience. In production use Alembic migrations.
    if settings.DEBUG:
        await init_db(create_tables=True)



