# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.init_db import init_db
from app.core.config import settings
import app.models  # ensure all models are imported so SQLAlchemy can resolve relationships

# MESSAGE-RELATED ROUTES
from app.routes.messages.send_message import router as send_message_router
from app.routes.messages.edit_message import router as edit_message_router
from app.routes.messages.delete_message import router as delete_message_router
from app.routes.messages.get_messages import router as get_messages_router
from app.routes.messages.update_last_read import router as update_last_read_router
from app.routes.messages.conversations import router as conversations_router
from app.routes.messages.reactions import router as reactions_router
from app.routes.friends.friends_requests import router as send_friend_request_router
from app.routes.friends.list_requests import router as list_friend_requests_router
from app.routes.friends.cancel_request import router as cancel_friend_request_router
from app.routes.friends.list_friends import router as friends_list_friends_router
from app.routes.friends.remove_friend import router as remove_friend_router
from app.routes.friends.respond_request import router as respond_request_router

from app.routes.auth.register import router as register_router
from app.routes.auth.login import router as login_router
from app.routes.auth.logout import router as logout_router
from app.routes.auth.refresh_token import router as refresh_router
from app.routes.auth.current_user import router as current_user_router
from app.routes.auth.google_callback import router as google_callback_router
from app.routes.auth.google_url import router as google_url_router

# USER ROUTES
from app.routes.users.update_avatar import router as update_avatar_router
# WEBSOCKET ROUTES
from app.websocket.router import router as websocket_router


app = FastAPI(title=settings.APP_NAME)

configured_origins = [origin.strip().rstrip("/") for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()]
if not configured_origins and settings.FRONTEND_URL:
    configured_origins = [settings.FRONTEND_URL.rstrip("/")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(send_message_router, tags=["messages"])
app.include_router(edit_message_router, tags=["messages"])
app.include_router(delete_message_router, tags=["messages"])
app.include_router(conversations_router, tags=["messages"])
app.include_router(reactions_router, tags=["reactions"])

# Conversations routes
app.include_router(get_messages_router, tags=["conversation_participants"])
app.include_router(update_last_read_router, tags=["conversation_participants"])
app.include_router(send_friend_request_router, tags=["friends"])
app.include_router(list_friend_requests_router, tags=["friends"])
app.include_router(cancel_friend_request_router, tags=["friends"])
app.include_router(friends_list_friends_router, tags=["friends"])
app.include_router(remove_friend_router, tags=["friends"])
app.include_router(respond_request_router, tags=["friends"])

# Websocket routes
app.include_router(websocket_router, tags=["websocket"])


app.include_router(register_router, tags=["auth"])
app.include_router(login_router, tags=["auth"])
app.include_router(logout_router, tags=["auth"])
app.include_router(refresh_router, tags=["auth"])
app.include_router(current_user_router, tags=["auth"])
app.include_router(google_url_router, tags=["auth"])
app.include_router(google_callback_router, tags=["auth"])

# User routes
app.include_router(update_avatar_router, tags=["users"])


@app.on_event("startup")
async def on_startup():
    # In development we create tables for convenience. In production use Alembic migrations.
    if settings.DEBUG:
        await init_db(create_tables=True)

