"""
Policy Module - Pure functions for return/refund eligibility
100% deterministic, no I/O, easy to unit test
"""
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.agent.models import Eligibility


# Policy configuration
POLICY_VERSION = "v1.0"
DEFAULT_RETURN_WINDOW_DAYS = 30
DEFAULT_REFUND_WINDOW_DAYS = 14

# Category-specific overrides
CATEGORY_OVERRIDES = {
    "electronics": {
        "return_days": 45,
        "refund_days": 14
    },
    "clothing": {
        "return_days": 60,
        "refund_days": 30
    }
}


def compute_days_since_delivery(delivery_date: Optional[datetime]) -> Optional[int]:
    """
    Compute days since delivery
    
    Args:
        delivery_date: Delivery date
        
    Returns:
        Number of days since delivery, or None if not delivered
    """
    if not delivery_date:
        return None
    
    now = datetime.utcnow()
    delta = now - delivery_date
    return delta.days


def get_policy_windows(category: Optional[str] = None) -> Dict[str, int]:
    """
    Get return and refund windows based on category
    
    Args:
        category: Product category
        
    Returns:
        Dict with return_days and refund_days
    """
    if category and category.lower() in CATEGORY_OVERRIDES:
        override = CATEGORY_OVERRIDES[category.lower()]
        return {
            "return_days": override["return_days"],
            "refund_days": override["refund_days"]
        }
    
    return {
        "return_days": DEFAULT_RETURN_WINDOW_DAYS,
        "refund_days": DEFAULT_REFUND_WINDOW_DAYS
    }


def check_eligibility(order: Dict[str, Any]) -> Eligibility:
    """
    Check return and refund eligibility for an order
    Pure function - no side effects
    
    Args:
        order: Order data with delivery_date, order_status, items, etc.
        
    Returns:
        Eligibility object with detailed information
    """
    # Extract order details
    delivery_date = order.get("delivery_date")
    order_status = order.get("status", "").lower()
    items = order.get("items", [])
    
    # Determine category (use first item's category if available)
    category = None
    if items and len(items) > 0:
        category = items[0].get("category")
    
    # Get policy windows
    windows = get_policy_windows(category)
    return_window_days = windows["return_days"]
    refund_window_days = windows["refund_days"]
    
    # Compute days since delivery
    days_since_delivery = compute_days_since_delivery(delivery_date)
    
    # Initialize result
    eligibility = Eligibility(
        policy_version=POLICY_VERSION,
        cutoff_days=return_window_days,  # Will be set properly below
        computed_days_since_delivery=days_since_delivery
    )
    
    # Check if order is in a valid state
    if order_status in ["cancelled", "refunded", "returned"]:
        eligibility.is_return_eligible = False
        eligibility.is_refund_eligible = False
        eligibility.reason = f"Order is already {order_status}"
        return eligibility
    
    # Check if order has been delivered
    if not delivery_date:
        eligibility.is_return_eligible = False
        eligibility.is_refund_eligible = False
        eligibility.reason = "Order has not been delivered yet"
        return eligibility
    
    # Check if delivery date is in the future (shouldn't happen, but defensive)
    if days_since_delivery is None or days_since_delivery < 0:
        eligibility.is_return_eligible = False
        eligibility.is_refund_eligible = False
        eligibility.reason = "Invalid delivery date"
        return eligibility
    
    # Check return eligibility
    if days_since_delivery <= return_window_days:
        eligibility.is_return_eligible = True
    else:
        eligibility.is_return_eligible = False
    
    # Check refund eligibility
    if days_since_delivery <= refund_window_days:
        eligibility.is_refund_eligible = True
    else:
        eligibility.is_refund_eligible = False
    
    # Set reason
    if eligibility.is_return_eligible and eligibility.is_refund_eligible:
        eligibility.reason = f"Within {return_window_days}-day return and {refund_window_days}-day refund window"
    elif eligibility.is_return_eligible:
        eligibility.reason = f"Within {return_window_days}-day return window (refund window expired)"
    elif eligibility.is_refund_eligible:
        eligibility.reason = f"Within {refund_window_days}-day refund window (return window expired)"
    else:
        eligibility.reason = f"Outside {return_window_days}-day return window"
    
    return eligibility


def format_eligibility_message(eligibility: Eligibility) -> str:
    """
    Format eligibility information into a user-friendly message
    
    Args:
        eligibility: Eligibility object
        
    Returns:
        Formatted message string
    """
    if eligibility.is_return_eligible and eligibility.is_refund_eligible:
        return (
            f"Good news! Your order qualifies for both a **return** and a **refund**. "
            f"It's been {eligibility.computed_days_since_delivery} days since delivery. "
            f"{eligibility.reason}."
        )
    elif eligibility.is_return_eligible:
        return (
            f"Your order qualifies for a **return**. "
            f"It's been {eligibility.computed_days_since_delivery} days since delivery. "
            f"{eligibility.reason}."
        )
    elif eligibility.is_refund_eligible:
        return (
            f"Your order qualifies for a **refund**. "
            f"It's been {eligibility.computed_days_since_delivery} days since delivery. "
            f"{eligibility.reason}."
        )
    else:
        return (
            f"Unfortunately, your order doesn't qualify for returns or refunds. "
            f"{eligibility.reason}. "
            f"It's been {eligibility.computed_days_since_delivery} days since delivery."
        )
