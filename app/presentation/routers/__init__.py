from .admin import router as admin_router
from .auth import router as auth_router
from .channel import router as channel_router
from .user import router as user_router
from .video import router as video_router
from .playlist import router as playlist_router

__all__ = ("admin_router", "auth_router", "channel_router", "user_router", "video_router","playlist_router")
