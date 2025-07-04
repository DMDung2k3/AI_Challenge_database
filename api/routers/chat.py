from fastapi import APIRouter, WebSocket, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
import asyncio
import json
import logging

# Import the models and service
from api.models.chat_models import ChatRequest, ChatResponse, ConversationHistoryResponse
from api.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter()
chat_service = ChatService()

# Simplified auth dependency for now - replace with actual auth implementation
async def get_current_user(token: Optional[str] = None):
    """Simplified auth dependency - replace with actual implementation"""
    # For now, return a mock user
    return {"id": "default_user", "username": "test_user"}

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, user=Depends(get_current_user)):
    """
    Process chat message and return AI response with video results.
    """
    try:
        response = await chat_service.process_message(request, user)
        return ChatResponse(**response)
    except Exception as e:
        logger.error(f"Error in send_message: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat streaming"""
    await websocket.accept()
    
    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()
            
            try:
                # Parse the incoming message
                message_data = json.loads(data)
                request = ChatRequest(
                    message=message_data.get("message", ""),
                    session_id=session_id,
                    user_id=message_data.get("user_id", "ws-user")
                )
                
                # Stream response back to client
                async for chunk in chat_service.stream_response(request, request.user_id):
                    await websocket.send_text(chunk)
                    
            except json.JSONDecodeError:
                # Handle plain text messages
                request = ChatRequest(
                    message=data,
                    session_id=session_id,
                    user_id="ws-user"
                )
                
                async for chunk in chat_service.stream_response(request, request.user_id):
                    await websocket.send_text(chunk)
                    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        error_message = {
            "type": "error",
            "content": f"Connection error: {str(e)}",
            "session_id": session_id,
            "is_final": True
        }
        try:
            await websocket.send_text(json.dumps(error_message))
        except:
            pass  # Connection might be closed
    finally:
        try:
            await websocket.close()
        except:
            pass

@router.get("/history/{session_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str, 
    limit: int = Query(50, ge=1, le=500, description="Number of messages to retrieve"),
    user=Depends(get_current_user)
):
    """Get conversation history for a session"""
    try:
        history_data = await chat_service.get_conversation_history(session_id, limit)
        return ConversationHistoryResponse(**history_data)
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/history/{session_id}")
async def clear_conversation_history(
    session_id: str,
    user=Depends(get_current_user)
):
    """Clear conversation history for a session"""
    try:
        result = await chat_service.clear_conversation(session_id)
        return result
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats")
async def get_chat_stats(user=Depends(get_current_user)):
    """Get chat service statistics"""
    try:
        stats = chat_service.get_service_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting chat stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """Health check endpoint for the chat service"""
    return {
        "status": "healthy",
        "service": "chat",
        "timestamp": asyncio.get_event_loop().time()
    }