# database/models/video_metadata.py - Temporary fix to match current database schema
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from .base import Base


class VideoMetadata(Base):
    __tablename__ = "video_metadata"
    
    # Core columns that exist in current database (from preprocess_videos.py)
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(String(255), unique=True, nullable=False)
    video_path = Column(String(1000))  # This exists as 'video_path' in current schema
    filename = Column(String(500))     # This exists in current schema
    uploaded_at = Column(DateTime, default=datetime.utcnow)  # This exists in current schema
    
    # Processing related columns (from preprocess_videos.py)
    processing_status = Column(String(50))
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    keyframes_extracted = Column(Integer)
    
    # Additional columns that should exist in full schema
    # Comment these out if they don't exist in your current database
    # title = Column(String(500))
    # description = Column(Text)
    # duration = Column(Float)  # in seconds
    # fps = Column(Float)
    # width = Column(Integer)
    # height = Column(Integer)
    # file_size = Column(Integer)  # in bytes
    # file_path = Column(String(1000))  # Different from video_path
    
    # Timestamps
    # created_at = Column(DateTime, default=datetime.utcnow)
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata as JSON
    # extra_metadata = Column(JSON)
    
    # Processing status
    # is_processed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<VideoMetadata(id={self.id}, video_id={self.video_id}, filename={self.filename})>"