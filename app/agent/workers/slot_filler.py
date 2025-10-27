"""
SlotFillerWorker (OrderNumberCollector)
Extracts or asks for order number
"""
import re
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.agent.models import AgentState


# Pattern for order numbers (e.g., ORD-123456, ABC123, etc.)
ORDER_NUMBER_PATTERN = re.compile(r'\b([A-Z0-9]{3}[-]?[0-9]{6,}|[0-9]{10,})\b')


EXTRACTION_PROMPT = """You are helping extract an order number from a customer message.
Order numbers typically look like: ORD-123456, ABC-123456, or similar alphanumeric codes.

If you find an order number in the message, respond with ONLY the order number.
If you don't find one, respond with ONLY the word "NONE".

Message: {message}
"""


async def slot_filler_worker(state: AgentState, llm: ChatOpenAI) -> Dict[str, Any]:
    """
    Extract or ask for order number
    
    Args:
        state: Current agent state
        llm: Language model instance
        
    Returns:
        Updated state with order_number or a question message
    """
    # Check if we already have an order number
    existing_order_number = state.get("order_number")
    if existing_order_number and len(existing_order_number) >= 6:
        return {}  # No changes needed
    
    # Get messages
    messages = state.get("messages", [])
    
    # Check if we JUST asked for order number (last assistant message asks for it)
    if messages and isinstance(messages[-1], AIMessage):
        last_msg_content = messages[-1].content.lower()
        if "order number" in last_msg_content:
            # We already asked, don't ask again - just return empty
            # This prevents infinite loop when user hasn't provided it yet
            return {}
    
    if not messages:
        return {
            "messages": messages + [AIMessage(content="I can help with that. What's your **order number**? It usually looks like **ORD-123456**.")]
        }
    
    # Try to extract from last user message (now HumanMessage objects)
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content
            break
    
    if not last_user_message:
        return {
            "messages": messages + [AIMessage(content="I can help with that. What's your **order number**? It usually looks like **ORD-123456**.")]
        }
    
    # Try regex extraction first
    match = ORDER_NUMBER_PATTERN.search(last_user_message)
    if match:
        order_number = match.group(1).upper()
        return {
            "order_number": order_number,
            "messages": messages + [AIMessage(content=f"Great! Let me look up order **{order_number}** for you...")]
        }
    
    # Try LLM extraction
    try:
        response = await llm.ainvoke([
            SystemMessage(content=EXTRACTION_PROMPT.format(message=last_user_message))
        ])
        
        extracted = response.content.strip().upper()
        
        if extracted != "NONE" and len(extracted) >= 6:
            return {
                "order_number": extracted,
                "messages": messages + [AIMessage(content=f"Great! Let me look up order **{extracted}** for you...")]
            }
    
    except Exception as e:
        print(f"Error in slot_filler_worker LLM extraction: {e}")
    
    # If we still don't have it, ask
    return {
        "messages": messages + [AIMessage(content="I need your order number to help you. It usually looks like **ORD-123456** or a similar code. Can you provide it?")]
    }
