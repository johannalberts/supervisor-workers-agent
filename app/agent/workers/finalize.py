"""
FinalizeWorker
Finalizes the conversation with templates (Zendesk-style)
"""
from typing import Dict, Any
import random
from langchain_core.messages import AIMessage
from app.agent.models import AgentState


# Template variations for different scenarios (Zendesk pattern)
ORDER_STATUS_CLOSING = [
    "Is there anything else I can help you with today?",
    "Do you need help with anything else?",
    "Can I assist you with anything else today?",
]

CANCEL_TEMPLATES = [
    "Thank you for contacting us. If you have any other questions, feel free to reach out!",
    "No problem! If you need anything else, we're here to help.",
    "Sounds good! Don't hesitate to reach out if you need assistance in the future.",
]

DENIAL_TEMPLATES = [
    "I'm sorry, but this order isn't eligible for {intent}. {reason}\n\nIf you have questions about our policy or need help with something else, I'm here to assist!",
    "Unfortunately, this order doesn't qualify for {intent}. {reason}\n\nLet me know if there's anything else I can help you with!",
    "I apologize, but we can't process a {intent} for this order. {reason}\n\nIs there something else I can do for you today?",
]

SUCCESS_RETURN_TEMPLATE = """✅ Perfect! I've created return ticket **{ticket_id}** for your order.{email_note}

**Next steps:**
1. Package your items securely
2. Print the return label from the email
3. Drop off at any authorized location

We'll process your return within 3-5 business days after we receive it. Thanks for your patience!"""

SUCCESS_REFUND_TEMPLATE = """✅ All done! I've created refund ticket **{ticket_id}** for your order.{email_note}

**Next steps:**
1. We'll process your refund within 3-5 business days
2. You'll receive the funds in your original payment method
3. You'll get an email confirmation once it's processed

Thank you for your patience!"""


async def finalize_worker(state: AgentState) -> Dict[str, Any]:
    """
    Finalize the conversation using templates
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final message
    """
    intent = state.get("intent")
    order = state.get("order")
    action_ticket = state.get("action_ticket", {})
    desired_action = state.get("desired_action")
    email_status = state.get("email_status")
    messages = state.get("messages", [])
    
    # Handle order_status intent - simple closing
    if intent == "order_status":
        final_message = random.choice(ORDER_STATUS_CLOSING)
        return {
            "messages": messages + [AIMessage(content=final_message)],
            "conversation_complete": True  # Flag to allow new intent classification
        }
    
    # Safely get ticket_id and email
    ticket_id = (action_ticket or {}).get("id", "Unknown")
    customer_email = order.get("customer_email", "your email") if order else "your email"
    
    # Mask email
    if "@" in customer_email:
        local, domain = customer_email.split("@", 1)
        if len(local) > 2:
            masked_email = f"{local[:2]}***@{domain}"
        else:
            masked_email = f"***@{domain}"
    else:
        masked_email = "***"
    
    # Handle explicit cancel
    if desired_action == "cancel":
        final_message = random.choice(CANCEL_TEMPLATES)
    
    # Handle case where no desired action was set (e.g., not eligible)
    elif not desired_action:
        eligibility = state.get("eligibility") or {}
        # If eligibility was computed and neither return nor refund is available
        if eligibility and not eligibility.get("is_return_eligible") and not eligibility.get("is_refund_eligible"):
            reason = eligibility.get("reason", "Not eligible under our policy.")
            intent_name = "return or refund"
            final_message = random.choice(DENIAL_TEMPLATES).format(
                intent=intent_name,
                reason=reason
            )
        else:
            # Generic fallback
            final_message = random.choice(ORDER_STATUS_CLOSING)
    
    else:
        # We have a desired action - use success templates
        email_note = ""
        if email_status == "sent":
            email_note = f" I've sent all the details to {masked_email}."
        elif email_status == "failed":
            email_note = " Note: There was an issue sending the email, but your ticket has been created."
        
        if desired_action == "return":
            final_message = SUCCESS_RETURN_TEMPLATE.format(
                ticket_id=ticket_id,
                email_note=email_note
            )
        elif desired_action == "refund":
            final_message = SUCCESS_REFUND_TEMPLATE.format(
                ticket_id=ticket_id,
                email_note=email_note
            )
        else:
            # Fallback
            final_message = f"✅ Done! I've created ticket {ticket_id} for your {desired_action} request.{email_note}"
    
    return {
        "messages": messages + [AIMessage(content=final_message)],
        "conversation_complete": True  # Flag to allow new intent classification
    }
