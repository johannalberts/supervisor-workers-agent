"""
PolicyCheckWorker
Checks return/refund eligibility using pure policy functions
"""
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.agent.models import AgentState
from app.agent.policy import check_eligibility


async def policy_check_worker(state: AgentState) -> Dict[str, Any]:
    """
    Check return/refund eligibility for the order
    Pure deterministic function - no I/O
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with eligibility information
    """
    order = state.get("order")
    if not order:
        return {
            "error": {
                "code": "NO_ORDER_DATA",
                "message": "No order data for policy check"
            }
        }
    
    try:
        # Run pure policy function
        eligibility = check_eligibility(order)
        
        # Convert to dict for state
        return {
            "eligibility": eligibility.model_dump()
        }
    
    except Exception as e:
        print(f"Error in policy_check_worker: {e}")
        return {
            "error": {
                "code": "POLICY_CHECK_ERROR",
                "message": str(e)
            }
        }
