"""
DecideActionWorker
Determines which action (return/refund) to take based on eligibility and user preference
"""
from typing import Dict, Any
from langchain_core.messages import AIMessage, HumanMessage
from app.agent.models import AgentState
from app.agent.policy import format_eligibility_message, Eligibility


async def decide_action_worker(state: AgentState) -> Dict[str, Any]:
    """
    Decide on return or refund action based on eligibility and user preference
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with desired_action or a question
    """
    eligibility_dict = state.get("eligibility", {})
    eligibility = Eligibility(**eligibility_dict)
    
    intent = state.get("intent")
    messages = state.get("messages", [])
    
    # Check if neither is eligible
    if not eligibility.is_return_eligible and not eligibility.is_refund_eligible:
        eligibility_msg = format_eligibility_message(eligibility)
        return {
            "desired_action": "cancel",
            "messages": messages + [AIMessage(content=f"{eligibility_msg} If you need further assistance, please contact our support team.")]
        }
    
    # Get last user message to check for preference
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content.lower()
            break
    
    # If only one is eligible, suggest that one
    if eligibility.is_return_eligible and not eligibility.is_refund_eligible:
        return {
            "desired_action": "return",
            "messages": messages + [AIMessage(content=f"{format_eligibility_message(eligibility)} I'll proceed with processing your return.")]
        }
    
    if eligibility.is_refund_eligible and not eligibility.is_return_eligible:
        return {
            "desired_action": "refund",
            "messages": messages + [AIMessage(content=f"{format_eligibility_message(eligibility)} I'll proceed with processing your refund.")]
        }
    
    # Both are eligible - check if user already indicated preference
    if last_user_message:
        if "return" in last_user_message and "refund" not in last_user_message:
            return {
                "desired_action": "return",
                "messages": messages + [AIMessage(content="Perfect! I'll process your return request.")]
            }
        elif "refund" in last_user_message and "return" not in last_user_message:
            return {
                "desired_action": "refund",
                "messages": messages + [AIMessage(content="Perfect! I'll process your refund request.")]
            }
    
    # Ask user to choose since both are eligible
    eligibility_msg = format_eligibility_message(eligibility)
    return {
        "messages": messages + [AIMessage(content=f"{eligibility_msg} Which would you like to proceed with? Please reply with **return** or **refund**.")]
    }
