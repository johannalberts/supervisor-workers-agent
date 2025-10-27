"""
OrderLookupWorker
Fetches order from MongoDB
"""
from typing import Dict, Any
from langchain_core.messages import AIMessage
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.agent.models import AgentState


async def order_lookup_worker(state: AgentState, db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """
    Look up order in database
    
    Args:
        state: Current agent state
        db: MongoDB database instance
        
    Returns:
        Updated state with order data or error
    """
    order_number = state.get("order_number")
    if not order_number:
        return {
            "error": {
                "code": "MISSING_ORDER_NUMBER",
                "message": "Order number is required"
            }
        }
    
    try:
        # Query MongoDB for the order (fixture data uses "order_number" field)
        print(f"[ORDER_LOOKUP] Searching for order: {order_number}")
        order = await db.orders.find_one({"order_number": order_number})
        
        print(f"[ORDER_LOOKUP] Query result: {order}")
        
        if not order:
            print(f"[ORDER_LOOKUP] ❌ Order {order_number} NOT FOUND in database")
            messages = state.get("messages", [])
            return {
                "error": {
                    "code": "ORDER_NOT_FOUND",
                    "message": f"Order {order_number} not found"
                },
                "messages": messages + [AIMessage(content=f"I couldn't find order **{order_number}** in our system. Please check the order number and try again.")]
            }
        
        # Normalize order data from fixture format
        normalized_order = {
            "order_id": order.get("order_number"),  # Use order_number from fixtures
            "customer_email": order.get("user_email"),  # Fixtures use user_email
            "first_name": order.get("first_name"),
            "last_name": order.get("last_name"),
            "contact_number": order.get("user_contact_number"),  # Fixtures use user_contact_number
            "items": order.get("items", []),
            "order_date": order.get("order_date"),
            "delivery_date": order.get("delivery_date"),
            "total_amount": order.get("order_total"),  # Fixtures use order_total
            "status": order.get("status", "unknown")
        }
        
        print(f"[ORDER_LOOKUP] ✅ Order found and normalized: {normalized_order['order_id']} for {normalized_order['first_name']} {normalized_order['last_name']}")
        
        return {
            "order": normalized_order,
            "order_match_confidence": 1.0
        }
    
    except Exception as e:
        print(f"Error in order_lookup_worker: {e}")
        messages = state.get("messages", [])
        return {
            "error": {
                "code": "DATABASE_ERROR",
                "message": str(e)
            },
            "messages": messages + [AIMessage(content="I'm having trouble accessing the order database. Please try again in a moment."
            )]
        }
