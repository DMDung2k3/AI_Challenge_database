from sqlalchemy import Column, String, DateTime, JSON, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict
import uuid

Base = declarative_base()

class UserSession(Base):
    """SQLAlchemy model for user session tracking."""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    current_topic = Column(String(500))
    current_video = Column(String(255))
    current_timestamp = Column(Float)
    active_entities = Column(JSON, default=list)
    mentioned_videos = Column(JSON, default=list)
    search_history = Column(JSON, default=list)
    user_preferences = Column(JSON, default=dict)
    start_time = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    conversation_turns = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class UserSessionPydantic(BaseModel):
    """Pydantic model for session validation."""
    id: str
    session_id: str
    user_id: str
    current_topic: Optional[str] = None
    current_video: Optional[str] = None
    current_timestamp: Optional[float] = None
    active_entities: Optional[List] = []
    mentioned_videos: Optional[List] = []
    search_history: Optional[List] = []
    user_preferences: Optional[Dict] = {}
    start_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    conversation_turns: Optional[int] = 0
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True