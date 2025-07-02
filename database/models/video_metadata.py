from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, VECTOR
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

Base = declarative_base()

class VideoMetadata(Base):
    """SQLAlchemy model for video metadata."""
    __tablename__ = "video_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(String(255), unique=True, nullable=False, index=True)
    video_path = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    duration = Column(Float)
    fps = Column(Float)
    resolution = Column(String(50))
    file_size = Column(Integer)
    processing_status = Column(String(50), default="pending")
    pipeline_id = Column(String(255))
    overall_quality_score = Column(Float)
    scenes_detected = Column(Integer)
    keyframes_extracted = Column(Integer)
    features_extracted = Column(Boolean, default=False)
    indexed = Column(Boolean, default=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    video_processing_result = Column(JSON)
    feature_extraction_result = Column(JSON)
    knowledge_graph_result = Column(JSON)
    indexing_result = Column(JSON)
    embedding = Column(VECTOR(384))  # Support for pgvector

class VideoMetadataPydantic(BaseModel):
    """Pydantic model for video metadata validation."""
    id: str
    video_id: str
    video_path: str
    filename: str
    duration: Optional[float] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    file_size: Optional[int] = None
    processing_status: Optional[str] = "pending"
    pipeline_id: Optional[str] = None
    overall_quality_score: Optional[float] = None
    scenes_detected: Optional[int] = None
    keyframes_extracted: Optional[int] = None
    features_extracted: Optional[bool] = False
    indexed: Optional[bool] = False
    uploaded_at: Optional[datetime] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    video_processing_result: Optional[dict] = None
    feature_extraction_result: Optional[dict] = None
    knowledge_graph_result: Optional[dict] = None
    indexing_result: Optional[dict] = None
    embedding: Optional[list] = None

    class Config:
        from_attributes = True