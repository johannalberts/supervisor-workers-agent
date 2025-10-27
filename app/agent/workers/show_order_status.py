"""
ShowOrderStatusWorker
Displays order status information to the user
"""
from typing import Dict, Any
from datetime import datetime
from langchain_core.messages import AIMessage
from app.agent.models import AgentState


def format_order_status(order: Dict[str, Any]) -> str:
    """
    Format order status details for display
    
    Args:
        order: Order data
        
    Returns:
        Formatted status message
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
    
    # Build status message
    status_message = f"""Here's the status of your order:

Order #{order_id}
• Status: {status}
• Order Date: {order_date_str}
• Delivery: {delivery_date_str}
• Total: ${total:.2f}
• Items: {total_items} item(s)
"""
    
    if tracking != "Not available":
        status_message += f"• Tracking: {tracking}\n"
    
    # Add status-specific messages
    if status.lower() == "delivered":
        status_message += "\n✅ Your order has been delivered! If you have any issues, please let us know."
    elif status.lower() == "shipped":
        status_message += "\n📦 Your order is on its way! Expected delivery soon."
    elif status.lower() == "processing":
        status_message += "\n⏳ Your order is being prepared for shipment."
    elif status.lower() == "pending":
        status_message += "\n📋 Your order has been received and will be processed shortly."
    
    return status_message


async def show_order_status_worker(state: AgentState) -> Dict[str, Any]:
    """
    Display order status information
    
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
