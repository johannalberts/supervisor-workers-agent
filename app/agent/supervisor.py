"""
Supervisor
Implements deterministic routing logic for the agent workflow
"""
from typing import Literal
from langchain_core.messages import AIMessage
from app.agent.models import AgentState


def supervisor_router(state: AgentState) -> Literal[
    "classify_intent", "slot_filler", "order_lookup", "confirm_details",
    "policy_check", "decide_action", "process_return", "process_refund",
    "send_email", "show_order_status", "finalize", "__end__"
]:
    """
    Routes to the appropriate worker based on state
    
    Args:
        state: Current agent state
        
    Returns:
        Name of next worker node to execute, or "__end__" to stop
    """
    print("\n=== SUPERVISOR ROUTING ===")
    print(f"Intent: {state.get('intent')}")
    print(f"Order Number: {state.get('order_number')}")
    print(f"Order: {state.get('order')}")
    print(f"User Confirmed: {state.get('user_confirmed_order')}")
    print(f"Eligibility: {state.get('eligibility')}")
    print(f"Desired Action: {state.get('desired_action')}")
    print(f"Action Ticket: {state.get('action_ticket')}")
    print(f"Email Status: {state.get('email_status')}")
    print(f"Error: {state.get('error')}")
    print(f"Messages count: {len(state.get('messages', []))}")
    
    # Check if there's an error - stop and wait for user to fix it
    if state.get("error"):
        print("→ Routing to: END (error occurred, waiting for user)")
        return "__end__"
    
    # Check if last message is from assistant (we just asked user something)
    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], AIMessage):
        last_content = messages[-1].content
        # If we just asked a question, stop here and wait for user response
        if "?" in last_content or "please" in last_content.lower():
            print("→ Routing to: END (waiting for user response)")
            return "__end__"
    
    # 1. First classify intent if not set
    if not state.get("intent"):
        print("→ Routing to: classify_intent (no intent)")
        return "classify_intent"
    
    # 2. Get order number if intent needs it (return/refund/order_status)
    intent = state.get("intent")
    if intent in ["return", "refund", "order_status"] and not state.get("order_number"):
        print("→ Routing to: slot_filler (need order number)")
        return "slot_filler"
    
    # 3. Look up order if we have order number but no order details
    if state.get("order_number") and not state.get("order"):
        print("→ Routing to: order_lookup (have order number, need order)")
        return "order_lookup"
    
    # 4. For order_status intent: go directly to show_order_status after lookup
    # But only if we haven't shown it yet (check if last message is from assistant with status info)
    if intent == "order_status" and state.get("order"):
        # Check if we already showed the status
        if messages and isinstance(messages[-1], AIMessage):
            last_msg = messages[-1].content.lower()
            # If last message contains status info, we already showed it - go to finalize
            if "status:" in last_msg or "order #" in last_msg or "delivery" in last_msg:
                print("→ Routing to: finalize (order status shown)")
                return "finalize"
        print("→ Routing to: show_order_status (order status check)")
        return "show_order_status"
    
    # 5. Confirm order details with user if not confirmed (for return/refund only)
    if state.get("order") and state.get("user_confirmed_order") is None and intent in ["return", "refund"]:
        print("→ Routing to: confirm_details (need confirmation)")
        return "confirm_details"
    
    # 6. If user declined, end conversation
    if state.get("user_confirmed_order") is False:
        print("→ Routing to: finalize (user declined)")
        return "finalize"
    
    # 7. Check policy eligibility if confirmed but not checked
    if state.get("user_confirmed_order") and not state.get("eligibility"):
        print("→ Routing to: policy_check (need eligibility check)")
        return "policy_check"
    
    # 8. Decide action if eligible but no decision made
    eligibility = state.get("eligibility", {})
    if eligibility.get("eligible") and not state.get("desired_action"):
        print("→ Routing to: decide_action (eligible, need action)")
        return "decide_action"
    
    # 9. If not eligible, finalize
    if eligibility and not eligibility.get("eligible"):
        print("→ Routing to: finalize (not eligible)")
        return "finalize"
    
    # 10. Process return if that's the desired action
    desired_action = state.get("desired_action")
    action_ticket = state.get("action_ticket", {})
    if desired_action == "return" and not action_ticket.get("id"):
        print("→ Routing to: process_return (processing return)")
        return "process_return"
    
    # 11. Process refund if that's the desired action
    if desired_action == "refund" and not action_ticket.get("id"):
        print("→ Routing to: process_refund (processing refund)")
        return "process_refund"
    
    # 12. Send email if we have a ticket but haven't sent email
    if action_ticket.get("id") and not state.get("email_status"):
        print("→ Routing to: send_email (have ticket, need email)")
        return "send_email"
    
    # 13. Finalize if email sent
    if state.get("email_status"):
        print("→ Routing to: finalize (email sent, finalizing)")
        return "finalize"
    
    # Default: if intent is "other", just finalize
    if intent == "other":
        print("→ Routing to: finalize (intent is other)")
        return "finalize"
    
    # Fallback: shouldn't reach here, but finalize if we do
    print("→ Routing to: finalize (fallback)")
    return "finalize"
