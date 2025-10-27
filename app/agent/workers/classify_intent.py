"""
ClassifyIntentWorker
Classifies user intent from their message
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.agent.models import AgentState


SYSTEM_PROMPT = """You are a customer service intent classifier. 
Your job is to determine if the user wants to:
- "return" (return a product/order)
- "refund" (get money back)
- "order_status" (check order status or tracking)
- "other" (something else)

Respond with ONLY ONE WORD: return, refund, order_status, or other.

Examples:
User: "I want to return my order" -> return
User: "Can I get a refund?" -> refund
User: "I'd like my money back" -> refund
User: "Send this back" -> return
User: "Where is my order?" -> order_status
User: "What's the status of my order?" -> order_status
User: "Track my package" -> order_status
User: "Has my order shipped?" -> order_status
User: "What's your phone number?" -> other
"""


async def classify_intent_worker(state: AgentState, llm: ChatOpenAI) -> Dict[str, Any]:
    """
    Classify the user's intent from their most recent message
    IMPORTANT: Only classifies if intent is not already set (for checkpoint resumption)
    
    Args:
        state: Current agent state
        llm: Language model instance
        
    Returns:
        Updated state with intent classification
    """
    # If we already have an intent (from checkpoint), don't re-classify
    # This prevents overwriting the intent when resuming from checkpoint
    existing_intent = state.get("intent")
    if existing_intent:
        print(f"[CLASSIFY_INTENT] Intent already set to '{existing_intent}', skipping classification")
        return {}  # Return empty dict - no changes needed
    
    # Get the last user message
    messages = state.get("messages", [])
    if not messages:
        return {"intent": "other"}
    
    # Find last user message (now LangChain HumanMessage objects)
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break
    
    if not last_user_message:
        return {"intent": "other"}
    
    # Call LLM to classify
    try:
        response = await llm.ainvoke([
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=last_user_message)
        ])
        
        intent = response.content.strip().lower()
        
        # Validate intent
        if intent not in ["return", "refund", "order_status", "other"]:
            intent = "other"
        
        print(f"[CLASSIFY_INTENT] Classified as: {intent}")
        return {"intent": intent}
    
    except Exception as e:
        print(f"Error in classify_intent_worker: {e}")
        return {"intent": "other"}
