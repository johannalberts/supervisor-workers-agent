"""
API Router
Handles all JSON API endpoints
"""
from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/api", tags=["api"])


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


@router.post("/chat", summary="Chat Endpoint")
async def chat(message: str) -> Dict[str, str]:
    """
    Chat endpoint for customer service bot
    This will be connected to the supervisor-workers agent system
    
    Args:
        message: User's chat message
        
    Returns:
        Bot's response message
    """
    # TODO: Connect to supervisor-workers agent system
    return {
        "response": f"You said: {message}. The agent system will be connected soon!",
        "status": "success"
    }
