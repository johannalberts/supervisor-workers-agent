"""
Agent State Models
Defines the state schema and data models for the LangGraph agent
"""
from typing import Optional, Literal, TypedDict, Annotated
from datetime import datetime
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class Eligibility(BaseModel):
    """Return/refund eligibility information"""
    is_return_eligible: Optional[bool] = None
    is_refund_eligible: Optional[bool] = None
    reason: Optional[str] = None
    policy_version: Optional[str] = None
    cutoff_days: Optional[int] = None
    computed_days_since_delivery: Optional[int] = None


class ActionTicket(BaseModel):
    """Ticket information for return/refund processing"""
    id: Optional[str] = None
    status: Optional[Literal["created", "duplicate", "failed"]] = None


class Meta(BaseModel):
    """Metadata for the conversation"""
    session_id: str
    idempotency_key: Optional[str] = None
    locale: str = "en"


class AgentState(TypedDict):
    """
    Main state for the customer service agent
    Single source of truth passed through all nodes
    """
    # Conversation history - MUST use add_messages reducer for checkpointing!
    # This tells LangGraph to APPEND new messages instead of replacing
    messages: Annotated[list, add_messages]
    
    # Intent classification
    intent: Optional[Literal["return", "refund", "other"]]
    
    # Order information
    order_number: Optional[str]
    order_match_confidence: Optional[float]
    order: Optional[dict]  # Normalized order data from DB
    user_confirmed_order: Optional[bool]
    
    # Eligibility assessment
    eligibility: dict  # Eligibility model as dict
    
    # Action decision
    desired_action: Optional[Literal["return", "refund", "cancel"]]
    
    # Processing
    action_ticket: dict  # ActionTicket model as dict
    
    # Communication
    email_status: Optional[Literal["sent", "failed"]]
    
    # Conversation flow control
    conversation_complete: Optional[bool]  # Flag to allow new intent after conversation ends
    
    # Error handling
    error: Optional[dict]  # {code: str, message: str}
    
    # Metadata
    meta: dict  # Meta model as dict


class Order(BaseModel):
    """Order model from database"""
    order_id: str
    customer_email: str
    first_name: str
    last_name: str
    contact_number: str
    items: list[dict]
    order_date: datetime
    delivery_date: Optional[datetime]
    total_amount: float
    status: str


class Message(BaseModel):
    """Chat message"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
