# database/models/user_session.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from .base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Additional session metadata
    session_metadata = Column(JSON)
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"