from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator
import logging
import asyncio
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Enum for conversation states"""
    ACTIVE = "active"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ConversationContext:
    """Context object for conversation state management"""
    session_id: str
    user_id: str
    conversation_history: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    state: ConversationState = ConversationState.ACTIVE
    

class BaseOrchestrator(ABC):
    """Abstract base class for conversation orchestrators"""
    
    @abstractmethod
    async def process(self, user_input: str, context: Optional[ConversationContext] = None) -> str:
        """Process user input and return response"""
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the orchestrator"""
        pass
    
    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup resources"""
        pass


class ConversationOrchestrator(BaseOrchestrator):
    """
    Main conversation orchestrator that handles:
    1. Intent understanding and preprocessing
    2. Context management
    3. Response generation
    4. Memory and state management
    """
    
    def __init__(self):
        self.context_store: Dict[str, ConversationContext] = {}
        self.is_initialized = False
        logger.info("ConversationOrchestrator initialized")
    
    async def initialize(self) -> None:
        """Initialize the orchestrator with required resources"""
        if self.is_initialized:
            return
        
        # TODO: Initialize NLP models, external APIs, etc.
        logger.info("Initializing ConversationOrchestrator resources...")
        
        # Placeholder for actual initialization
        await asyncio.sleep(0.1)  # Simulate initialization time
        
        self.is_initialized = True
        logger.info("ConversationOrchestrator initialized successfully")
    
    async def cleanup(self) -> None:
        """Cleanup resources and connections"""
        logger.info("Cleaning up ConversationOrchestrator resources...")
        self.context_store.clear()
        self.is_initialized = False
        logger.info("ConversationOrchestrator cleanup completed")
    
    async def process(self, user_input: str, context: Optional[ConversationContext] = None) -> str:
        """
        Process user input through the following pipeline:
        1. Preprocess and understand intent
        2. Fetch required data (DB/cache/external APIs)
        3. Generate contextual response
        4. Update conversation state
        """
        if not self.is_initialized:
            await self.initialize()
        
        try:
            # Step 1: Preprocess input
            processed_input = await self._preprocess_input(user_input)
            
            # Step 2: Understand intent
            intent_data = await self._analyze_intent(processed_input)
            
            # Step 3: Fetch required data
            context_data = await self._fetch_context_data(intent_data, context)
            
            # Step 4: Generate response
            response = await self._generate_response(processed_input, intent_data, context_data)
            
            # Step 5: Update conversation state
            await self._update_conversation_state(user_input, response, context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return f"I apologize, but I encountered an error processing your request. Please try again."
    
    async def _preprocess_input(self, user_input: str) -> str:
        """Preprocess user input (cleanup, normalization, etc.)"""
        # Basic preprocessing
        cleaned_input = user_input.strip()
        
        # TODO: Add more sophisticated preprocessing
        # - Remove special characters
        # - Normalize text
        # - Handle multiple languages
        
        return cleaned_input
    
    async def _analyze_intent(self, processed_input: str) -> Dict[str, Any]:
        """Analyze user intent and extract relevant information"""
        # TODO: Implement proper intent analysis
        # For now, return basic intent structure
        
        intent_data = {
            "intent": "general_query",
            "entities": [],
            "confidence": 0.8,
            "keywords": processed_input.lower().split()
        }
        
        # Basic intent classification
        if any(word in processed_input.lower() for word in ["hello", "hi", "hey"]):
            intent_data["intent"] = "greeting"
        elif any(word in processed_input.lower() for word in ["bye", "goodbye", "exit"]):
            intent_data["intent"] = "farewell"
        elif "?" in processed_input:
            intent_data["intent"] = "question"
        
        return intent_data
    
    async def _fetch_context_data(self, intent_data: Dict[str, Any], context: Optional[ConversationContext]) -> Dict[str, Any]:
        """Fetch relevant data from databases, cache, or external APIs"""
        context_data = {
            "user_history": [],
            "relevant_docs": [],
            "external_data": {}
        }
        
        # TODO: Implement actual data fetching
        # - Query databases based on intent
        # - Fetch from cache
        # - Call external APIs
        # - Retrieve user conversation history
        
        if context:
            context_data["session_id"] = context.session_id
            context_data["user_id"] = context.user_id
            context_data["user_history"] = context.conversation_history[-5:]  # Last 5 messages
        
        return context_data
    
    async def _generate_response(self, user_input: str, intent_data: Dict[str, Any], context_data: Dict[str, Any]) -> str:
        """Generate appropriate response based on intent and context"""
        intent = intent_data.get("intent", "general_query")
        
        # Handle different intents
        if intent == "greeting":
            return self._generate_greeting_response(context_data)
        elif intent == "farewell":
            return self._generate_farewell_response()
        elif intent == "question":
            return await self._generate_question_response(user_input, context_data)
        else:
            return await self._generate_general_response(user_input, intent_data, context_data)
    
    def _generate_greeting_response(self, context_data: Dict[str, Any]) -> str:
        """Generate greeting response"""
        user_id = context_data.get("user_id")
        if user_id:
            return f"Hello! How can I help you today?"
        return "Hello! How can I assist you?"
    
    def _generate_farewell_response(self) -> str:
        """Generate farewell response"""
        return "Goodbye! Feel free to come back anytime if you need help."
    
    async def _generate_question_response(self, user_input: str, context_data: Dict[str, Any]) -> str:
        """Generate response for questions"""
        # TODO: Implement proper question answering
        return f"That's an interesting question about '{user_input}'. Let me think about that..."
    
    async def _generate_general_response(self, user_input: str, intent_data: Dict[str, Any], context_data: Dict[str, Any]) -> str:
        """Generate general response"""
        # TODO: Implement more sophisticated response generation
        # - Use language models
        # - Template-based responses
        # - Context-aware generation
        
        return f"I understand you're saying: '{user_input}'. How can I help you with this?"
    
    async def _update_conversation_state(self, user_input: str, response: str, context: Optional[ConversationContext]) -> None:
        """Update conversation state and history"""
        if context:
            # Add to conversation history
            context.conversation_history.append({
                "timestamp": asyncio.get_event_loop().time(),
                "user_input": user_input,
                "bot_response": response,
                "state": context.state.value
            })
            
            # Update context store
            self.context_store[context.session_id] = context
    
    async def get_or_create_context(self, session_id: str, user_id: str) -> ConversationContext:
        """Get existing context or create new one"""
        if session_id in self.context_store:
            return self.context_store[session_id]
        
        # Create new context
        context = ConversationContext(
            session_id=session_id,
            user_id=user_id,
            conversation_history=[],
            metadata={}
        )
        
        self.context_store[session_id] = context
        return context
    
    async def clear_context(self, session_id: str) -> None:
        """Clear conversation context for a session"""
        if session_id in self.context_store:
            del self.context_store[session_id]
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about current conversations"""
        return {
            "active_sessions": len(self.context_store),
            "total_messages": sum(len(ctx.conversation_history) for ctx in self.context_store.values()),
            "session_states": {
                state.value: len([ctx for ctx in self.context_store.values() if ctx.state == state])
                for state in ConversationState
            }
        }


# ChatService class to interface with the orchestrator
class ChatService:
    """Service layer for handling chat operations"""
    
    def __init__(self):
        self.orchestrator = ConversationOrchestrator()
        logger.info("ChatService initialized")
    
    async def process_message(self, request, user) -> Dict[str, Any]:
        """Process a chat message and return response"""
        try:
            # Extract message and session info from request
            message = getattr(request, 'message', '')
            session_id = getattr(request, 'session_id', f"session_{user.get('id', 'unknown')}")
            user_id = str(user.get('id', 'unknown'))
            
            # Get or create conversation context
            context = await self.orchestrator.get_or_create_context(session_id, user_id)
            
            # Process the message
            response = await self.orchestrator.process(message, context)
            
            return {
                "message": response,
                "session_id": session_id,
                "user_id": user_id,
                "timestamp": asyncio.get_event_loop().time(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in ChatService.process_message: {e}")
            return {
                "message": "I apologize, but I encountered an error processing your request.",
                "session_id": getattr(request, 'session_id', 'unknown'),
                "user_id": str(user.get('id', 'unknown')),
                "timestamp": asyncio.get_event_loop().time(),
                "status": "error",
                "error": str(e)
            }
    
    async def stream_response(self, request, user_id: str) -> AsyncGenerator[str, None]:
        """Stream response for WebSocket connections"""
        try:
            # Simulate streaming response
            message = getattr(request, 'message', '')
            session_id = getattr(request, 'session_id', f"session_{user_id}")
            
            # Get or create conversation context
            context = await self.orchestrator.get_or_create_context(session_id, user_id)
            
            # Process the message
            response = await self.orchestrator.process(message, context)
            
            # Stream the response word by word
            words = response.split()
            for i, word in enumerate(words):
                chunk = {
                    "type": "message_chunk",
                    "content": word + " ",
                    "chunk_id": i,
                    "session_id": session_id,
                    "is_final": i == len(words) - 1
                }
                yield json.dumps(chunk)
                await asyncio.sleep(0.1)  # Simulate typing delay
                
        except Exception as e:
            error_chunk = {
                "type": "error",
                "content": f"Error: {str(e)}",
                "session_id": getattr(request, 'session_id', 'unknown'),
                "is_final": True
            }
            yield json.dumps(error_chunk)
    
    async def get_conversation_history(self, session_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get conversation history for a session"""
        try:
            if session_id in self.orchestrator.context_store:
                context = self.orchestrator.context_store[session_id]
                history = context.conversation_history[-limit:]
                return {
                    "history": history,
                    "session_id": session_id,
                    "total_messages": len(context.conversation_history),
                    "status": "success"
                }
            else:
                return {
                    "history": [],
                    "session_id": session_id,
                    "total_messages": 0,
                    "status": "success"
                }
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return {
                "history": [],
                "session_id": session_id,
                "total_messages": 0,
                "status": "error",
                "error": str(e)
            }
    
    async def clear_conversation(self, session_id: str) -> Dict[str, Any]:
        """Clear conversation history for a session"""
        try:
            await self.orchestrator.clear_context(session_id)
            return {
                "message": "Conversation cleared successfully",
                "session_id": session_id,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
            return {
                "message": "Error clearing conversation",
                "session_id": session_id,
                "status": "error",
                "error": str(e)
            }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return self.orchestrator.get_conversation_stats()