"""
FinalizeWorker
Finalizes the conversation with a summary
"""
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.agent.models import AgentState


async def finalize_worker(state: AgentState) -> Dict[str, Any]:
    """
    Finalize the conversation with a summary
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final message
    """
    order = state.get("order")
    action_ticket = state.get("action_ticket", {})
    desired_action = state.get("desired_action")
    email_status = state.get("email_status")
    messages = state.get("messages", [])
    
    ticket_id = action_ticket.get("id", "Unknown")
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
    
    # Build final message
    if desired_action == "cancel":
        final_message = "Thank you for contacting us. If you have any other questions, feel free to reach out!"
    else:
        email_note = ""
        if email_status == "sent":
            email_note = f" I've emailed **{masked_email}** with the details and next steps."
        elif email_status == "failed":
            email_note = " Note: There was an issue sending the confirmation email, but your ticket has been created."
        
        final_message = (
            f"✅ All done! I've created a **{desired_action}** ticket **{ticket_id}** for your order.{email_note}\n\n"
            f"**Next steps:**\n"
        )
        
        if desired_action == "return":
            final_message += (
                "1. Package your items securely\n"
                "2. Print the return label from the email\n"
                "3. Drop off at any authorized location\n\n"
                "We'll process your return within 3-5 business days after we receive it."
            )
        elif desired_action == "refund":
            final_message += (
                "1. We'll process your refund within 3-5 business days\n"
                "2. You'll receive the funds in your original payment method\n"
                "3. You'll get an email confirmation once it's processed\n\n"
                "Thank you for your patience!"
            )
    
    return {
        "messages": messages + [AIMessage(content=final_message
        )]
    }
