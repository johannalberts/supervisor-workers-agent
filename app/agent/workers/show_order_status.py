"""
ShowOrderStatusWorker
Displays order status information using templates (Zendesk-style)
"""
from typing import Dict, Any
from datetime import datetime
import random
from langchain_core.messages import AIMessage
from app.agent.models import AgentState


# Status-specific message templates (Zendesk pattern)
STATUS_MESSAGES = {
    "delivered": [
        "✅ Great news! Your order has been delivered. If you have any issues with your items, please let me know!",
        "✅ Your order was successfully delivered! Everything should be there. Let me know if you need anything else.",
        "✅ Delivery confirmed! Your order has arrived. If something's not right, I'm here to help!",
    ],
    "shipped": [
        "📦 Excellent! Your order is on its way and should arrive soon.",
        "📦 Your order has shipped and is currently in transit. Delivery is coming up!",
        "📦 Good news — your order is out for delivery and will be with you shortly!",
    ],
    "processing": [
        "⏳ Your order is currently being prepared for shipment. We'll have it on its way soon!",
        "⏳ We're processing your order right now. It should ship within the next day or two.",
        "⏳ Your order is being packed and will ship out very soon!",
    ],
    "pending": [
        "📋 Your order has been received and will be processed shortly.",
        "📋 Thanks for your order! We've got it and will start processing soon.",
        "📋 Order confirmed! We'll begin processing it right away.",
    ],
}


def format_order_status(order: Dict[str, Any]) -> str:
    """
    Format order status details using templates
    
    Args:
        order: Order data
        
    Returns:
        Formatted status message string
    """
    order_id = order.get("order_id", "Unknown")
    order_date = order.get("order_date")
    delivery_date = order.get("delivery_date")
    status = order.get("status", "unknown").title()
    items = order.get("items", [])
    total = order.get("total_amount", 0)
    tracking = order.get("tracking_number", "Not available")
    
    # Format dates
    if isinstance(order_date, datetime):
        order_date_str = order_date.strftime("%B %d, %Y")
    else:
        order_date_str = "Unknown"
    
    if isinstance(delivery_date, datetime):
        delivery_date_str = delivery_date.strftime("%B %d, %Y")
        delivery_status = "Delivered"
    else:
        delivery_date_str = "Not yet delivered"
        delivery_status = "In transit"
    
    # Count items
    total_items = sum(item.get("quantity", 1) for item in items)
    
    # Build status message using template
    status_message = f"""Here's the status of your order:

**Order #{order_id}**
• Status: {status}
• Order Date: {order_date_str}
• Delivery: {delivery_date_str}
• Total: ${total:.2f}
• Items: {total_items} item(s)"""
    
    if tracking != "Not available":
        status_message += f"\n• Tracking: {tracking}"
    
    # Add status-specific message from template variations
    status_key = status.lower()
    if status_key in STATUS_MESSAGES:
        status_note = random.choice(STATUS_MESSAGES[status_key])
        status_message += f"\n\n{status_note}"
    
    return status_message


async def show_order_status_worker(state: AgentState) -> Dict[str, Any]:
    """
    Display order status information using templates
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with status message
    """
    order = state.get("order")
    if not order:
        return {
            "error": {
                "code": "NO_ORDER_DATA",
                "message": "No order data to display"
            }
        }
    
    messages = state.get("messages", [])
    status_message = format_order_status(order)
    
    return {
        "messages": messages + [AIMessage(content=status_message)]
    }
