"""
ProcessRefundWorker
Creates refund ticket
"""
import hashlib
from typing import Dict, Any
from langchain_core.messages import AIMessage
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.agent.models import AgentState


async def process_refund_worker(state: AgentState, db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """
    Process refund request and create refund ticket
    Idempotent - returns same ticket for duplicate requests
    
    Args:
        state: Current agent state
        db: MongoDB database instance
        
    Returns:
        Updated state with action_ticket
    """
    order = state.get("order")
    if not order:
        return {
            "error": {
                "code": "NO_ORDER_DATA",
                "message": "No order data for refund processing"
            }
        }
    
    order_id = order.get("order_id")
    desired_action = state.get("desired_action")
    
    # Generate idempotency key
    idempotency_key = hashlib.sha256(f"{order_id}|{desired_action}".encode()).hexdigest()
    
    try:
        # Check if ticket already exists (idempotency)
        existing_ticket = await db.action_tickets.find_one({
            "idempotency_key": idempotency_key
        })
        
        if existing_ticket:
            return {
                "action_ticket": {
                    "id": existing_ticket.get("ticket_id"),
                    "status": "duplicate"
                },
                "meta": {
                    **state.get("meta", {}),
                    "idempotency_key": idempotency_key
                }
            }
        
        # Create new refund ticket
        ticket_id = f"REF-{datetime.utcnow().strftime('%Y%m%d')}-{order_id}"
        
        ticket_doc = {
            "ticket_id": ticket_id,
            "idempotency_key": idempotency_key,
            "order_id": order_id,
            "action": desired_action,
            "status": "created",
            "created_at": datetime.utcnow(),
            "customer_email": order.get("customer_email"),
            "refund_amount": order.get("total_amount")
        }
        
        await db.action_tickets.insert_one(ticket_doc)
        
        messages = state.get("messages", [])
        return {
            "action_ticket": {
                "id": ticket_id,
                "status": "created"
            },
            "meta": {
                **state.get("meta", {}),
                "idempotency_key": idempotency_key
            },
            "messages": messages + [AIMessage(content=f"Great! I've created refund ticket **{ticket_id}** for your order.")]
        }
    
    except Exception as e:
        print(f"Error in process_refund_worker: {e}")
        messages = state.get("messages", [])
        return {
            "action_ticket": {
                "id": None,
                "status": "failed"
            },
            "error": {
                "code": "REFUND_PROCESSING_ERROR",
                "message": str(e)
            },
            "messages": messages + [AIMessage(content="I encountered an error while creating your refund ticket. Please try again."
            )]
        }
