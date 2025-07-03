# database/models/conversation.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from .base import Base

class ConversationHistory(Base):
    """SQLAlchemy model for conversation history tracking."""
    __tablename__ = "conversation_history"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    turn_id = Column(String(255), nullable=False)

    # Message content
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)

    # Analysis results
    intent = Column(String(100), nullable=True)
    entities = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    video_references = Column(JSON, default=list)

    # Quality metrics
    satisfaction_score = Column(Float, nullable=True)
    resolved = Column(Boolean, default=False)
    processing_time = Column(Float, default=0.0)

    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow)
