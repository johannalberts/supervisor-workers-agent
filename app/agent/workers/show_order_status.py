"""
ShowOrderStatusWorker
Displays order status information to the user
"""
from typing import Dict, Any
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from app.agent.models import AgentState


def format_order_status(order: Dict[str, Any]) -> Dict[str, str]:
    """
    Format order status details for display
    
    Args:
        order: Order data
        
    Returns:
        Dictionary with formatted fields for LLM to use
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
    
    # Return structured data for LLM
    return {
        "order_id": order_id,
        "status": status,
        "order_date": order_date_str,
        "delivery_date": delivery_date_str,
        "total": f"${total:.2f}",
        "items_count": total_items,
        "tracking": tracking,
        "is_delivered": status.lower() == "delivered",
        "is_shipped": status.lower() == "shipped",
        "is_processing": status.lower() == "processing",
        "is_pending": status.lower() == "pending"
    }


async def show_order_status_worker(state: AgentState, llm: ChatOpenAI = None) -> Dict[str, Any]:
    """
    Display order status information with natural language
    
    Args:
        state: Current agent state
        llm: Language model instance for generating responses
        
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
    status_data = format_order_status(order)
    
    if llm:
        # Generate natural language status message
        status_prompt = f"""Generate a friendly, informative message about the customer's order status.

Order details:
- Order #: {status_data['order_id']}
- Status: {status_data['status']}
- Order Date: {status_data['order_date']}
- Delivery Date: {status_data['delivery_date']}
- Total: {status_data['total']}
- Items: {status_data['items_count']} item(s)
- Tracking: {status_data['tracking']}

Guidelines:
- Be conversational and friendly
- Present the information clearly with bullet points
- Add a status-specific message at the end:
  * If delivered: Express happiness and offer help if needed
  * If shipped: Build excitement about upcoming delivery
  * If processing: Reassure them it's being prepared
  * If pending: Confirm order received and processing will start soon
- Use appropriate emojis (✅ 📦 ⏳ 📋) to match the status
- Keep it concise (3-5 sentences plus bullet points)"""
        
        response = await llm.ainvoke([
            SystemMessage(content=status_prompt),
            HumanMessage(content=f"Show status for order {status_data['order_id']}")
        ])
        status_message = response.content
    else:
        # Fallback to template
        status_message = f"""Here's the status of your order:

Order #{status_data['order_id']}
• Status: {status_data['status']}
• Order Date: {status_data['order_date']}
• Delivery: {status_data['delivery_date']}
• Total: {status_data['total']}
• Items: {status_data['items_count']} item(s)"""
        
        if status_data['tracking'] != "Not available":
            status_message += f"\n• Tracking: {status_data['tracking']}"
    
    return {
        "messages": messages + [AIMessage(content=status_message)]
    }
