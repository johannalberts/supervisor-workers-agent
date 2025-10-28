"""
FinalizeWorker
Finalizes the conversation with a summary
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from app.agent.models import AgentState


async def finalize_worker(state: AgentState, llm: ChatOpenAI = None) -> Dict[str, Any]:
    """
    Finalize the conversation with a natural language summary
    
    Args:
        state: Current agent state
        llm: Language model instance for generating responses
        
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
        if llm:
            closing_prompt = """Generate a brief, friendly closing message (1 sentence) that:
- Offers further assistance
- Sounds natural and warm
Keep it conversational."""
            
            response = await llm.ainvoke([
                SystemMessage(content=closing_prompt),
                HumanMessage(content="Order status inquiry completed")
            ])
            final_message = response.content
        else:
            final_message = "Is there anything else I can help you with today?"
        
        return {
            "messages": messages + [AIMessage(content=final_message)]
        }
    
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
    
    # Prepare context for LLM
    context = {
        "intent": intent,
        "desired_action": desired_action,
        "ticket_id": ticket_id,
        "email": masked_email,
        "email_status": email_status
    }
    
    # Handle explicit cancel
    if desired_action == "cancel":
        if llm:
            cancel_prompt = """Generate a brief, friendly closing message (1-2 sentences) that:
- Thanks them for contacting us
- Invites them to reach out again if needed
Keep it warm and professional."""
            
            response = await llm.ainvoke([
                SystemMessage(content=cancel_prompt),
                HumanMessage(content="User cancelled the request")
            ])
            final_message = response.content
        else:
            final_message = "Thank you for contacting us. If you have any other questions, feel free to reach out!"
    
    # Handle case where no desired action was set (e.g., not eligible)
    elif not desired_action:
        eligibility = state.get("eligibility") or {}
        # If eligibility was computed and neither return nor refund is available
        if eligibility and not eligibility.get("is_return_eligible") and not eligibility.get("is_refund_eligible"):
            reason = eligibility.get("reason", "Not eligible under our policy.")
            
            if llm:
                denial_prompt = f"""Generate an empathetic denial message (2-3 sentences) that:
- Apologizes sincerely
- Explains why: {reason}
- Offers to help with other questions if they have any
Be understanding and professional."""
                
                response = await llm.ainvoke([
                    SystemMessage(content=denial_prompt),
                    HumanMessage(content=f"Order not eligible for return/refund: {reason}")
                ])
                final_message = response.content
            else:
                final_message = f"I'm sorry — this order isn't eligible for return or refund. Reason: {reason}"
        else:
            # Generic fallback
            if llm:
                fallback_prompt = """Generate a brief closing message (1 sentence) that:
- Thanks them
- Offers further assistance
Keep it professional."""
                
                response = await llm.ainvoke([
                    SystemMessage(content=fallback_prompt),
                    HumanMessage(content="Completed check")
                ])
                final_message = response.content
            else:
                final_message = "Thank you. We've completed the check. If you need further help, please let us know."
    
    else:
        # We have a desired action and should summarize the created ticket
        if llm:
            success_prompt = f"""Generate a comprehensive success message (3-4 sentences + bullet points) that:
- Celebrates the completion (✅)
- States the {desired_action} ticket {ticket_id} has been created
- Mentions email sent to {masked_email} (if email_status is 'sent')
- Provides clear next steps in bullet points:
  * For return: Package securely, print label, drop off
  * For refund: Processing time (3-5 days), original payment method
- Ends on a positive, helpful note

Keep it friendly, clear, and professional. Use formatting like ** for emphasis."""
            
            email_context = f"Email status: {email_status}" if email_status else "No email sent yet"
            
            response = await llm.ainvoke([
                SystemMessage(content=success_prompt),
                HumanMessage(content=f"Created {desired_action} ticket {ticket_id}. {email_context}")
            ])
            final_message = response.content
        else:
            # Fallback to template
            email_note = ""
            if email_status == "sent":
                email_note = f" I've emailed {masked_email} with the details and next steps."
            elif email_status == "failed":
                email_note = " Note: There was an issue sending the confirmation email, but your ticket has been created."

            final_message = (
                f"✅ All done! I've created a {desired_action} ticket {ticket_id} for your order.{email_note}\n\n"
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
        "messages": messages + [AIMessage(content=final_message)]
    }
