from .friends_requests import router as send_request_router
from .list_requests import router as list_requests_router
from .cancel_request import router as cancel_request_router
from .list_friends import router as list_friends_router
from .remove_friend import router as remove_friend_router
from .respond_request import router as respond_request_router

__all__ = [
    "send_request_router",
    "list_requests_router",
    "cancel_request_router",
    "list_friends_router",
    "remove_friend_router",
    "respond_request_router",
]
