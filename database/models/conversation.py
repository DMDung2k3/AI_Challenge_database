from sqlalchemy import Column, String, JSON, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict
import uuid

Base = declarative_base()

class Conversation(Base):
    """SQLAlchemy model for conversation history."""
    __tablename__ = "conversation_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    turn_id = Column(String(255), nullable=False)
    user_message = Column(String, nullable=False)
    assistant_response = Column(String, nullable=False)
    intent = Column(String(100))
    entities = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    video_references = Column(JSON, default=list)
    satisfaction_score = Column(Float)
    resolved = Column(Boolean, default=False)
    processing_time = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ConversationPydantic(BaseModel):
    """Pydantic model for conversation validation."""
    id: str
    session_id: str
    turn_id: str
    user_message: str
    assistant_response: str
    intent: Optional[str] = None
    entities: Optional[List] = []
    topics: Optional[List] = []
    video_references: Optional[List] = []
    satisfaction_score: Optional[float] = None
    resolved: Optional[bool] = False
    processing_time: Optional[float] = None
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True