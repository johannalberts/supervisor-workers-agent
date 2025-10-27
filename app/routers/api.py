"""
API Router
Handles all JSON API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.core.database import get_database
from app.services.agent_service import AgentService

router = APIRouter(prefix="/api", tags=["api"])


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    messages: List[str]
    session_id: str
    success: bool
    state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.get("/health", summary="Health Check")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify API is running
    
    Returns:
        Dictionary with status and message
    """
    return {
        "status": "healthy",
        "message": "API is running"
    }


@router.get("/data", summary="Get Sample Data")
async def get_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Sample API endpoint returning JSON data
    
    Returns:
        Dictionary containing a list of sample items
    """
    return {
        "items": [
            {"id": 1, "name": "Item 1", "description": "First item"},
            {"id": 2, "name": "Item 2", "description": "Second item"},
            {"id": 3, "name": "Item 3", "description": "Third item"},
        ]
    }


@router.post("/chat", response_model=ChatResponse, summary="Chat Endpoint")
async def chat(request: ChatRequest, db = Depends(get_database)) -> ChatResponse:
    """
    Chat endpoint for customer service bot
    Connected to the supervisor-workers agent system
    
    Args:
        request: Chat request with message and optional session_id
        db: Database connection
        
    Returns:
        Bot's response message(s) and session info
    """
    try:
        # Initialize agent service
        agent_service = AgentService(db)
        
        # Get or create session
        session_id = request.session_id
        if not session_id:
            session_id = await agent_service.create_session()
        
        # Process the message
        result = await agent_service.process_message(session_id, request.message)
        
        return ChatResponse(
            messages=result.get("messages", []),
            session_id=session_id,
            success=result.get("success", True),
            state=result.get("state"),
            error=result.get("error")
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/history", summary="Get Conversation History")
async def get_history(session_id: str, db = Depends(get_database)) -> Dict[str, Any]:
    """
    Get conversation history for a session
    
    Args:
        session_id: Session ID
        db: Database connection
        
    Returns:
        Conversation history
    """
    try:
        agent_service = AgentService(db)
        messages = await agent_service.get_conversation_history(session_id)
        
        return {
            "session_id": session_id,
            "messages": messages
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

