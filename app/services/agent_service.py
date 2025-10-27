"""
Agent Service
Handles graph execution and session management
"""
import uuid
from typing import Dict, List, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.checkpoint.base import CheckpointTuple
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.agent.models import AgentState, Meta, Eligibility, ActionTicket
from app.agent.graph import create_agent_graph
from app.core.config import settings
from app.core.database import get_checkpointer


# Global singleton graph instance (Zendesk pattern)
_graph_instance = None
_graph_initialized = False


def get_or_create_graph(db: AsyncIOMotorDatabase):
    """
    Get or create the singleton graph instance (enterprise pattern)
    Created once at first request, reused forever
    """
    global _graph_instance, _graph_initialized
    
    if not _graph_initialized:
        print("[AGENT_SERVICE] Creating singleton graph instance (Zendesk pattern)")
        llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.0,
            api_key=settings.openai_api_key
        )
        checkpointer = get_checkpointer()
        _graph_instance = create_agent_graph(llm, db, checkpointer)
        _graph_initialized = True
        print("[AGENT_SERVICE] ✅ Singleton graph created and cached for all requests")
    
    return _graph_instance


class AgentService:
    """
    Service for managing agent conversations with LangGraph checkpointing
    Uses singleton graph pattern for enterprise-scale performance
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize the agent service
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        # Get the singleton graph instance (created once, reused forever)
        self.graph = get_or_create_graph(db)
    
    async def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new conversation session
        
        Args:
            user_id: Optional user ID
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        # Initialize session in database
        session_doc = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "state": self._get_initial_state(session_id)
        }
        
        await self.db.conversation_sessions.insert_one(session_doc)
        
        return session_id
    
    def _get_initial_state(self, session_id: str) -> AgentState:
        """
        Get initial state for a new session
        
        Args:
            session_id: Session ID
            
        Returns:
            Initial agent state
        """
        return {
            "messages": [],
            "intent": None,
            "order_number": None,
            "order_match_confidence": None,
            "order": None,
            "user_confirmed_order": None,
            "eligibility": {},
            "desired_action": None,
            "action_ticket": {},
            "email_status": None,
            "error": None,
            "meta": {
                "session_id": session_id,
                "idempotency_key": None,
                "locale": "en"
            }
        }
    
    async def get_session_state(self, session_id: str) -> Optional[AgentState]:
        """
        Retrieve session state from database
        
        Args:
            session_id: Session ID
            
        Returns:
            Agent state or None if not found
        """
        session = await self.db.conversation_sessions.find_one({
            "session_id": session_id
        })
        
        if not session:
            return None
        
        return session.get("state")
    
    async def save_session_state(self, session_id: str, state: AgentState):
        """
        Save session state to database
        
        Args:
            session_id: Session ID
            state: Agent state to save
        """
        await self.db.conversation_sessions.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "state": state,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    async def process_message(
        self,
        session_id: str,
        message: str
    ) -> Dict[str, any]:
        """
        Process a user message through the agent graph with checkpointing
        
        Args:
            session_id: Session ID (used as thread_id for checkpointer)
            message: User message
            
        Returns:
            Response with assistant messages
        """
        print(f"[AGENT_SERVICE] Processing message for session: {session_id}")
        
        # Create a LangChain message object (required for checkpointer to work!)
        # The checkpointer needs proper LangChain message types to append to state
        input_message = HumanMessage(content=message)
        
        print(f"[AGENT_SERVICE] Invoking graph with checkpointing (thread_id={session_id})")
        print(f"[AGENT_SERVICE] Input: new message only (checkpointer will load rest)")
        
        # Run the graph with checkpointing config
        try:
            # The config with thread_id tells the checkpointer which conversation to resume
            config = {
                "configurable": {"thread_id": session_id},
                "recursion_limit": 50
            }
            
            # Invoke with ONLY the new message - checkpointer handles state loading
            # Messages in input are APPENDED to existing messages from checkpoint
            # All other state fields should be loaded from checkpoint automatically
            result = await self.graph.ainvoke(
                {"messages": [input_message]},
                config=config
            )
            
            print(f"[AGENT_SERVICE] Graph execution complete")
            print(f"[AGENT_SERVICE] Result state: intent={result.get('intent')}, order_number={result.get('order_number')}, has_order={result.get('order') is not None}")
            print(f"[AGENT_SERVICE] Total messages in state: {len(result.get('messages', []))}")
            
            # Extract assistant messages that came after the user message
            all_messages = result.get("messages", [])
            assistant_messages = []
            
            # Find messages after our HumanMessage
            found_our_message = False
            for msg in all_messages:
                # Check if this is our HumanMessage
                if isinstance(msg, HumanMessage) and msg.content == message:
                    found_our_message = True
                    continue
                
                # Collect AIMessages that come after our message
                if found_our_message and isinstance(msg, AIMessage):
                    assistant_messages.append(msg.content)
            
            return {
                "success": True,
                "messages": assistant_messages,
                "state": {
                    "intent": result.get("intent"),
                    "order_number": result.get("order_number"),
                    "has_order": result.get("order") is not None,
                    "desired_action": result.get("desired_action"),
                    "ticket_id": result.get("action_ticket", {}).get("id")
                }
            }
        
        except Exception as e:
            print(f"Error processing message: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "messages": ["I encountered an error processing your request. Please try again."],
                "error": str(e)
            }
    
    async def get_conversation_history(
        self,
        session_id: str
    ) -> List[Dict[str, str]]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of messages
        """
        state = await self.get_session_state(session_id)
        
        if not state:
            return []
        
        return state.get("messages", [])
