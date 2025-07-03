# database/models/processing_job.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from .base import Base

class ProcessingJob(Base):
    """SQLAlchemy model for background processing job tracking."""
    __tablename__ = "processing_jobs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String(255), unique=True, nullable=False, index=True)
    job_type = Column(String(100), nullable=False)  # single_video, batch_video

    # Job details
    input_data = Column(JSON, default=dict)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    progress = Column(Float, default=0.0)

    # Results
    result_data = Column(JSON, default=dict)
    error_message = Column(Text, nullable=True)

    # Metrics
    total_items = Column(Integer, nullable=True)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)