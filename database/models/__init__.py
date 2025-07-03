# database/models/__init__.py

# import Base để Alembic có thể thấy metadata
from .base import Base

# import các model để Base.metadata bao gồm tất cả
from .user_session import UserSession
from .conversation import ConversationHistory
from .video_metadata import VideoMetadata
from .processing_job import ProcessingJob

__all__ = [
    "Base",
    "UserSession",
    "ConversationHistory",
    "VideoMetadata",
    "ProcessingJob",
]
