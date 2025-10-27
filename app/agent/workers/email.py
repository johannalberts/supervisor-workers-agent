"""
EmailWorker
Sends confirmation email (mock implementation)
"""
from typing import Dict, Any
from app.agent.models import AgentState


async def email_worker(state: AgentState) -> Dict[str, Any]:
    """
    Send confirmation email
    In production, this would integrate with an email service
    For now, it's a mock that always succeeds
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with email_status
    """
    order = state.get("order")
    action_ticket = state.get("action_ticket", {})
    desired_action = state.get("desired_action")
    
    if not order or not action_ticket.get("id"):
        return {
            "email_status": "failed",
            "error": {
                "code": "EMAIL_MISSING_DATA",
                "message": "Missing order or ticket data for email"
            }
        }
    
    customer_email = order.get("customer_email")
    ticket_id = action_ticket.get("id")
    
    try:
        # Mock email sending
        # In production: await email_service.send(customer_email, template, data)
        
        print(f"[MOCK EMAIL] To: {customer_email}")
        print(f"[MOCK EMAIL] Subject: Your {desired_action} request #{ticket_id}")
        print(f"[MOCK EMAIL] Body: Your {desired_action} request has been created. Ticket ID: {ticket_id}")
        
        # Simulate success
        return {
            "email_status": "sent"
        }
    
    except Exception as e:
        print(f"Error in email_worker: {e}")
        return {
            "email_status": "failed",
            "error": {
                "code": "EMAIL_SEND_ERROR",
                "message": str(e)
            }
        }
