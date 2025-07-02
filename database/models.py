from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base  # Sử dụng từ sqlalchemy.orm
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()  # Không cần thay đổi dòng này, chỉ cần đảm bảo import đúng

class VideoMetadata(Base):
    """
    Metadata của videos được process bởi PreprocessingOrchestrator
    """
    __tablename__ = "video_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(String(255), unique=True, nullable=False, index=True)
    video_path = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    
    # Video properties
    duration = Column(Float)
    fps = Column(Float)
    resolution = Column(String(50))
    file_size = Column(Integer)
    
    # Processing status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    pipeline_id = Column(String(255))
    
    # Quality metrics
    overall_quality_score = Column(Float)
    scenes_detected = Column(Integer)
    keyframes_extracted = Column(Integer)
    features_extracted = Column(Boolean, default=False)
    indexed = Column(Boolean, default=False)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # Processing results (JSON data)
    video_processing_result = Column(JSON)
    feature_extraction_result = Column(JSON) 
    knowledge_graph_result = Column(JSON)
    indexing_result = Column(JSON)

class UserSession(Base):
    """
    User sessions cho ContextManagerAgent
    """
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    
    # Session state
    current_topic = Column(String(500))
    current_video = Column(String(255))
    current_timestamp = Column(Float)
    
    # Context data (JSON)
    active_entities = Column(JSON, default=list)
    mentioned_videos = Column(JSON, default=list)
    search_history = Column(JSON, default=list)
    user_preferences = Column(JSON, default=dict)
    
    # Session info
    start_time = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    conversation_turns = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class ConversationHistory(Base):
    """
    Conversation history cho context tracking
    """
    __tablename__ = "conversation_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, index=True)
    turn_id = Column(String(255), nullable=False)
    
    # Message content
    user_message = Column(Text, nullable=False)
    assistant_response = Column(Text, nullable=False)
    
    # Analysis results
    intent = Column(String(100))
    entities = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    video_references = Column(JSON, default=list)
    
    # Quality metrics
    satisfaction_score = Column(Float)
    resolved = Column(Boolean, default=False)
    processing_time = Column(Float)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)

class ProcessingJob(Base):
    """
    Background processing jobs tracking
    """
    __tablename__ = "processing_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String(255), unique=True, nullable=False, index=True)
    job_type = Column(String(100), nullable=False)  # single_video, batch_video
    
    # Job details
    input_data = Column(JSON)  # Video paths, config, etc.
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    progress = Column(Float, default=0.0)  # 0.0 to 1.0
    
    # Results
    result_data = Column(JSON)
    error_message = Column(Text)
    
    # Metrics
    total_items = Column(Integer)
    processed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

# Helper functions để work với models
def create_all_tables(engine):
    """Tạo tất cả tables"""
    Base.metadata.create_all(bind=engine)

def get_video_by_id(session, video_id: str) -> VideoMetadata:
    """Lấy video metadata by ID"""
    return session.query(VideoMetadata).filter(
        VideoMetadata.video_id == video_id
    ).first()

def update_video_processing_status(session, video_id: str, status: str, result_data: dict = None):
    """Update video processing status"""
    video = get_video_by_id(session, video_id)
    if video:
        video.processing_status = status
        if status == "processing" and not video.processing_started_at:
            video.processing_started_at = datetime.utcnow()
        elif status == "completed":
            video.processing_completed_at = datetime.utcnow()
            if result_data:
                # Update results based on type
                for key, value in result_data.items():
                    if hasattr(video, key):
                        setattr(video, key, value)
        session.commit()

def save_conversation_turn(session, session_id: str, turn_data: dict):
    """Save conversation turn"""
    turn = ConversationHistory(
        session_id=session_id,
        turn_id=turn_data.get("turn_id", f"turn_{datetime.utcnow().timestamp()}"),
        user_message=turn_data.get("user_message", ""),
        assistant_response=turn_data.get("assistant_response", ""),
        intent=turn_data.get("intent", ""),
        entities=turn_data.get("entities", []),
        topics=turn_data.get("topics", []),
        video_references=turn_data.get("video_references", []),
        processing_time=turn_data.get("processing_time", 0)
    )
    session.add(turn)
    session.commit()
    return turn