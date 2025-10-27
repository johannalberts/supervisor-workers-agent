"""
ConfirmDetailsWorker
Confirms order details with the user
"""
from typing import Dict, Any
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from app.agent.models import AgentState


def format_order_summary(order: Dict[str, Any]) -> str:
    """
    Format order details into a detailed summary with bullet points
    
    Args:
        order: Order data
        
    Returns:
        Formatted summary string with bullet points
    """
    order_id = order.get("order_id", "Unknown")
    order_date = order.get("order_date")
    delivery_date = order.get("delivery_date")
    items = order.get("items", [])
    email = order.get("customer_email", "")
    total = order.get("total_amount", 0)
    
    # Format date
    if isinstance(order_date, datetime):
        date_str = order_date.strftime("%B %d, %Y")
    else:
        date_str = "Unknown date"
    
    # Format delivery date
    if isinstance(delivery_date, datetime):
        delivery_str = delivery_date.strftime("%B %d, %Y")
    else:
        delivery_str = "Unknown"
    
    # Format items as bullet list
    items_list = []
    if items:
        for item in items:
            name = item.get("product_name", "Unknown item")
            qty = item.get("quantity", 1)
            price = item.get("unit_price", 0)
            items_list.append(f"  • {name} (x{qty}) - ${price:.2f}")
    
    items_str = "\n".join(items_list) if items_list else "  • No items"
    
    # Mask email
    if "@" in email:
        local, domain = email.split("@", 1)
        if len(local) > 2:
            masked_email = f"{local[:2]}***@{domain}"
        else:
            masked_email = f"***@{domain}"
    else:
        masked_email = "***"
    
    return f"""I found your order:

Order #{order_id}
• Order Date: {date_str}
• Delivery Date: {delivery_str}
• Total: ${total:.2f}
• Email: {masked_email}

Items:
{items_str}

Is this the correct order?"""


async def confirm_details_worker(state: AgentState) -> Dict[str, Any]:
    """
    Ask user to confirm order details
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with confirmation request or confirmed status
    """
    order = state.get("order")
    if not order:
        return {
            "error": {
                "code": "NO_ORDER_DATA",
                "message": "No order data to confirm"
            }
        }
    
    # Check if we already have confirmation
    user_confirmed = state.get("user_confirmed_order")
    if user_confirmed is not None:
        return {}  # Already handled
    
    messages = state.get("messages", [])
    
    # Check if we already asked for confirmation (prevent duplicate asks)
    if messages and isinstance(messages[-1], AIMessage):
        last_ai_msg = messages[-1].content.lower()
        if "is this the correct order" in last_ai_msg or "please reply with" in last_ai_msg:
            # We already asked, don't ask again
            return {}
    
    # Check if the last user message contains a yes/no response
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content.lower()
            break
    
    # If we just looked up the order, ask for confirmation
    if last_user_message and ("yes" in last_user_message or "correct" in last_user_message or "yep" in last_user_message or "yeah" in last_user_message):
        return {
            "user_confirmed_order": True,
            "messages": messages + [AIMessage(content="Perfect! Let me check what options are available for your order...")]
        }
    elif last_user_message and ("no" in last_user_message or "wrong" in last_user_message or "incorrect" in last_user_message):
        return {
            "user_confirmed_order": False,
            "order_number": None,  # Reset to ask again
            "order": None,
            "messages": messages + [AIMessage(content="I apologize for the confusion. Let's start over. What's your correct order number?")]
        }
    
    # First time - ask for confirmation
    order_summary = format_order_summary(order)
    return {
        "messages": messages + [AIMessage(content=f"{order_summary}\n\nPlease reply 'yes' to confirm or 'no' if this isn't your order.")]
    }
