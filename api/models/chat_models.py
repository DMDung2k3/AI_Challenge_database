from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="The user's message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(None, description="User ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how can you help me?",
                "session_id": "session_123",
                "user_id": "user_456",
                "metadata": {"source": "web"}
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat messages"""
    message: str = Field(..., description="The AI's response message")
    session_id: str = Field(..., description="Session ID")
    user_id: str = Field(..., description="User ID")
    timestamp: float = Field(..., description="Response timestamp")
    status: str = Field(..., description="Response status")
    error: Optional[str] = Field(None, description="Error message if any")
    video_results: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Video search results")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello! I'm here to help you. What would you like to know?",
                "session_id": "session_123",
                "user_id": "user_456",
                "timestamp": 1640995200.0,
                "status": "success",
                "error": None,
                "video_results": []
            }
        }


class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history"""
    history: List[Dict[str, Any]] = Field(..., description="Conversation history")
    session_id: str = Field(..., description="Session ID")
    total_messages: int = Field(..., description="Total number of messages")
    status: str = Field(..., description="Response status")
    error: Optional[str] = Field(None, description="Error message if any")
    
    class Config:
        json_schema_extra = {
            "example": {
                "history": [
                    {
                        "timestamp": 1640995200.0,
                        "user_input": "Hello",
                        "bot_response": "Hi there!",
                        "state": "active"
                    }
                ],
                "session_id": "session_123",
                "total_messages": 2,
                "status": "success",
                "error": None
            }
        }


class StreamChunk(BaseModel):
    """Model for streaming response chunks"""
    type: str = Field(..., description="Type of chunk (message_chunk, error, etc.)")
    content: str = Field(..., description="Chunk content")
    chunk_id: Optional[int] = Field(None, description="Chunk sequence ID")
    session_id: str = Field(..., description="Session ID")
    is_final: bool = Field(False, description="Whether this is the final chunk")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "message_chunk",
                "content": "Hello ",
                "chunk_id": 0,
                "session_id": "session_123",
                "is_final": False
            }
        }


class ChatServiceStats(BaseModel):
    """Model for chat service statistics"""
    active_sessions: int = Field(..., description="Number of active sessions")
    total_messages: int = Field(..., description="Total number of messages processed")
    session_states: Dict[str, int] = Field(..., description="Count of sessions by state")
    
    class Config:
        json_schema_extra = {
            "example": {
                "active_sessions": 5,
                "total_messages": 150,
                "session_states": {
                    "active": 3,
                    "waiting": 1,
                    "completed": 1,
                    "error": 0
                }
            }
        }