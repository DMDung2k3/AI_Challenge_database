from typing import Dict, Any, Optional
import json
import time
from datetime import datetime, timedelta
import tenacity
import logging
from database.connections.vector_db import VectorDB
from database.connections.graph_db import GraphDB
from database.connections.metadata_db import MetadataDB
from database.connections.cache_db import CacheDB
from database.models.video_metadata import VideoMetadata, VideoMetadataPydantic
from database.models.user_session import UserSession, UserSessionPydantic
from database.models.conversation import Conversation, ConversationPydantic
from database.models.processing_job import ProcessingJob, ProcessingJobPydantic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentDatabaseIntegration:
    """Helper class to integrate agents with database."""
    
    def __init__(self):
        self.vector_db = VectorDB()
        self.graph_db = GraphDB()
        self.metadata_db = MetadataDB()
        self.cache_db = CacheDB()
        self.sql_session = self.metadata_db.get_session()

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        retry=tenacity.retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: logger.warning(f"Retrying database operation: attempt {retry_state.attempt_number}")
    )
    def save_preprocessing_result(self, video_path: str, pipeline_result: Dict[str, Any]):
        """Save preprocessing result into database."""
        try:
            video_id = pipeline_result.get("video_id")
            
            # Check Bloom filter
            if self.cache_db.check_bloom(video_id):
                logger.info(f"Skipping already processed video: {video_id}")
                return None
            
            # Update or create video metadata
            video = self.sql_session.query(VideoMetadata).filter(
                VideoMetadata.video_id == video_id
            ).first()
            
            if not video:
                video = VideoMetadata(
                    video_id=video_id,
                    video_path=video_path,
                    filename=video_path.split("/")[-1]
                )
                self.sql_session.add(video)
            
            # Update processing results
            video.processing_status = pipeline_result.get("status", "completed")
            video.overall_quality_score = pipeline_result.get("overall_quality_score", 0)
            video.pipeline_id = pipeline_result.get("pipeline_id")
            video.video_processing_result = pipeline_result.get("video_processing_result")
            video.feature_extraction_result = pipeline_result.get("feature_extraction_result")
            video.knowledge_graph_result = pipeline_result.get("knowledge_graph_result")
            video.indexing_result = pipeline_result.get("indexing_result")
            video.features_extracted = video.feature_extraction_result is not None
            video.indexed = video.indexing_result is not None
            if pipeline_result.get("status") == "completed":
                video.processing_completed_at = datetime.utcnow()
            
            self.sql_session.commit()
            
            # Cache video info in Redis
            self.cache_db.setex(
                f"video:{video_id}",
                3600,  # 1 hour TTL
                json.dumps({
                    "video_id": video_id,
                    "status": video.processing_status,
                    "indexed": video.indexed,
                    "quality_score": video.overall_quality_score
                })
            )
            self.cache_db.add_to_bloom(video_id)
            
            return str(video.id)
            
        except Exception as e:
            self.sql_session.rollback()
            logger.error(f"Failed to save preprocessing result: {e}")
            raise

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        retry=tenacity.retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: logger.warning(f"Retrying database operation: attempt {retry_state.attempt_number}")
    )
    def load_session_context(self, session_id: str, user_id: str):
        """Load session context from database."""
        try:
            # Load from database
            session = self.sql_session.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if not session:
                session = UserSession(
                    session_id=session_id,
                    user_id=user_id
                )
                self.sql_session.add(session)
                self.sql_session.commit()
            
            # Load conversation history
            conversation_history = self.sql_session.query(Conversation).filter(
                Conversation.session_id == session_id
            ).order_by(Conversation.timestamp.desc()).limit(10).all()
            
            # Convert to SessionContext format
            from agents.conversational.context_manager_agent import SessionContext, ConversationTurn
            
            turns = []
            for conv in conversation_history:
                turn = ConversationTurn(
                    turn_id=conv.turn_id,
                    timestamp=conv.timestamp.isoformat(),
                    user_message=conv.user_message,
                    assistant_response=conv.assistant_response,
                    intent=conv.intent or "",
                    entities=conv.entities or [],
                    topics=conv.topics or [],
                    video_references=conv.video_references or []
                )
                turns.append(turn)
            
            session_context = SessionContext(
                session_id=session.session_id,
                user_id=session.user_id,
                start_time=session.start_time.isoformat(),
                current_topic=session.current_topic,
                current_video=session.current_video,
                current_timestamp=session.current_timestamp,
                active_entities=session.active_entities or [],
                mentioned_videos=session.mentioned_videos or [],
                search_history=session.search_history or [],
                conversation_turns=turns
            )
            
            return session_context
            
        except Exception as e:
            logger.error(f"Failed to load session context: {e}")
            raise

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
        retry=tenacity.retry_if_exception_type(Exception),
        before_sleep=lambda retry_state: logger.warning(f"Retrying database operation: attempt {retry_state.attempt_number}")
    )
    def save_conversation_result(self, session_id: str, conversation_flow: Dict[str, Any]):
        """Save conversation result after ConversationOrchestrator completes."""
        try:
            # Update session
            session = self.sql_session.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if session:
                session.last_activity = datetime.utcnow()
                session.conversation_turns += 1
                
                if "context_updates" in conversation_flow:
                    context_data = conversation_flow["context_updates"]
                    updated_context = context_data.get("updated_context", {})
                    session.current_topic = updated_context.get("current_topic")
                    session.current_video = updated_context.get("current_video") 
                    session.active_entities = updated_context.get("active_entities", [])
                    session.mentioned_videos = updated_context.get("mentioned_videos", [])
                    session.search_history = updated_context.get("search_history", [])
            
            # Save conversation turn
            if "query_understanding" in conversation_flow and "final_response" in conversation_flow:
                turn_data = {
                    "turn_id": f"turn_{int(time.time())}",
                    "user_message": conversation_flow.get("user_query", ""),
                    "assistant_response": conversation_flow["final_response"].get("main_answer", ""),
                    "intent": conversation_flow["query_understanding"].get("intent", {}).get("intent_type", ""),
                    "entities": [e.get("entity_text", "") for e in conversation_flow["query_understanding"].get("entities", [])],
                    "video_references": [r.get("video_id", "") for r in conversation_flow.get("retrieval_results", {}).get("results", [])],
                    "processing_time": conversation_flow.get("total_execution_time", 0)
                }
                
                turn = Conversation(**turn_data, session_id=session_id)
                self.sql_session.add(turn)
            
            self.sql_session.commit()
            
        except Exception as e:
            self.sql_session.rollback()
            logger.error(f"Failed to save conversation result: {e}")
            raise

    def get_indexed_videos(self) -> list:
        """Get list of indexed and ready-to-search videos."""
        try:
            videos = self.sql_session.query(VideoMetadata).filter(
                VideoMetadata.indexed == True,
                VideoMetadata.processing_status == "completed"
            ).all()
            
            return [{
                "video_id": v.video_id,
                "video_path": v.video_path,
                "quality_score": v.overall_quality_score,
                "duration": v.duration
            } for v in videos]
            
        except Exception as e:
            logger.error(f"Failed to get indexed videos: {e}")
            raise

    def cleanup_old_sessions(self, days: int = 7):
        """Cleanup old sessions."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            self.sql_session.query(Conversation).filter(
                Conversation.timestamp < cutoff_date
            ).delete()
            
            self.sql_session.query(UserSession).filter(
                UserSession.last_activity < cutoff_date
            ).update({"is_active": False})
            
            self.sql_session.commit()
            
        except Exception as e:
            self.sql_session.rollback()
            logger.error(f"Failed to cleanup old sessions: {e}")
            raise