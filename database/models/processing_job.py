from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict
import uuid

Base = declarative_base()

class ProcessingJob(Base):
    """SQLAlchemy model for background processing jobs."""
    __tablename__ = "processing_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String(255), unique=True, nullable=False, index=True)
    job_type = Column(String(100), nullable=False)
    input_data = Column(JSON)
    status = Column(String(50), default="pending")
    progress = Column(Float, default=0.0)
    result_data = Column(JSON)
    error_message = Column(Text)
    total_items = Column(Integer)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

class ProcessingJobPydantic(BaseModel):
    """Pydantic model for processing job validation."""
    id: str
    job_id: str
    job_type: str
    input_data: Optional[Dict] = None
    status: Optional[str] = "pending"
    progress: Optional[float] = 0.0
    result_data: Optional[Dict] = None
    error_message: Optional[str] = None
    total_items: Optional[int] = None
    processed_items: Optional[int] = 0
    failed_items: Optional[int] = 0
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True