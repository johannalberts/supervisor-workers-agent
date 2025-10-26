"""
MongoDB Database Fixtures
Sample customer orders for testing and development
"""
from datetime import datetime, timedelta


# Sample customer orders
SAMPLE_ORDERS = [
    {
        "order_number": "ORD-2024-001",
        "first_name": "John",
        "last_name": "Smith",
        "user_email": "john.smith@example.com",
        "user_contact_number": "+1-555-0101",
        "items": [
            {
                "product_id": "PROD-001",
                "product_name": "Wireless Headphones",
                "quantity": 1,
                "unit_price": 79.99,
                "total_price": 79.99
            },
            {
                "product_id": "PROD-002",
                "product_name": "USB-C Cable",
                "quantity": 2,
                "unit_price": 12.99,
                "total_price": 25.98
            }
        ],
        "order_total": 105.97,
        "order_date": datetime(2024, 10, 15, 10, 30, 0),
        "delivery_date": datetime(2024, 10, 18, 14, 0, 0),
        "status": "delivered"
    },
    {
        "order_number": "ORD-2024-002",
        "first_name": "Sarah",
        "last_name": "Johnson",
        "user_email": "sarah.johnson@example.com",
        "user_contact_number": "+1-555-0102",
        "items": [
            {
                "product_id": "PROD-003",
                "product_name": "Laptop Stand",
                "quantity": 1,
                "unit_price": 45.00,
                "total_price": 45.00
            }
        ],
        "order_total": 45.00,
        "order_date": datetime(2024, 10, 16, 14, 15, 0),
        "delivery_date": datetime(2024, 10, 20, 10, 0, 0),
        "status": "delivered"
    },
    {
        "order_number": "ORD-2024-003",
        "first_name": "Michael",
        "last_name": "Brown",
        "user_email": "michael.brown@example.com",
        "user_contact_number": "+1-555-0103",
        "items": [
            {
                "product_id": "PROD-004",
                "product_name": "Mechanical Keyboard",
                "quantity": 1,
                "unit_price": 129.99,
                "total_price": 129.99
            },
            {
                "product_id": "PROD-005",
                "product_name": "Gaming Mouse",
                "quantity": 1,
                "unit_price": 59.99,
                "total_price": 59.99
            },
            {
                "product_id": "PROD-006",
                "product_name": "Mouse Pad",
                "quantity": 1,
                "unit_price": 19.99,
                "total_price": 19.99
            }
        ],
        "order_total": 209.97,
        "order_date": datetime(2024, 10, 18, 9, 45, 0),
        "delivery_date": datetime(2024, 10, 22, 16, 0, 0),
        "status": "in_transit"
    },
    {
        "order_number": "ORD-2024-004",
        "first_name": "Emily",
        "last_name": "Davis",
        "user_email": "emily.davis@example.com",
        "user_contact_number": "+1-555-0104",
        "items": [
            {
                "product_id": "PROD-007",
                "product_name": "Webcam HD",
                "quantity": 1,
                "unit_price": 89.99,
                "total_price": 89.99
            },
            {
                "product_id": "PROD-008",
                "product_name": "Ring Light",
                "quantity": 1,
                "unit_price": 34.99,
                "total_price": 34.99
            }
        ],
        "order_total": 124.98,
        "order_date": datetime(2024, 10, 19, 11, 20, 0),
        "delivery_date": datetime(2024, 10, 23, 12, 0, 0),
        "status": "processing"
    },
    {
        "order_number": "ORD-2024-005",
        "first_name": "David",
        "last_name": "Wilson",
        "user_email": "david.wilson@example.com",
        "user_contact_number": "+1-555-0105",
        "items": [
            {
                "product_id": "PROD-009",
                "product_name": "Bluetooth Speaker",
                "quantity": 2,
                "unit_price": 49.99,
                "total_price": 99.98
            },
            {
                "product_id": "PROD-010",
                "product_name": "Phone Case",
                "quantity": 1,
                "unit_price": 24.99,
                "total_price": 24.99
            }
        ],
        "order_total": 124.97,
        "order_date": datetime(2024, 10, 20, 15, 30, 0),
        "delivery_date": datetime(2024, 10, 25, 10, 0, 0),
        "status": "delivered"
    },
    {
        "order_number": "ORD-2024-006",
        "first_name": "Lisa",
        "last_name": "Martinez",
        "user_email": "lisa.martinez@example.com",
        "user_contact_number": "+1-555-0106",
        "items": [
            {
                "product_id": "PROD-011",
                "product_name": "External SSD 1TB",
                "quantity": 1,
                "unit_price": 119.99,
                "total_price": 119.99
            }
        ],
        "order_total": 119.99,
        "order_date": datetime(2024, 10, 21, 8, 0, 0),
        "delivery_date": datetime(2024, 10, 26, 14, 0, 0),
        "status": "in_transit"
    },
    {
        "order_number": "ORD-2024-007",
        "first_name": "Robert",
        "last_name": "Taylor",
        "user_email": "robert.taylor@example.com",
        "user_contact_number": "+1-555-0107",
        "items": [
            {
                "product_id": "PROD-012",
                "product_name": "Monitor 27 inch",
                "quantity": 1,
                "unit_price": 299.99,
                "total_price": 299.99
            },
            {
                "product_id": "PROD-013",
                "product_name": "HDMI Cable",
                "quantity": 1,
                "unit_price": 15.99,
                "total_price": 15.99
            },
            {
                "product_id": "PROD-014",
                "product_name": "Monitor Arm",
                "quantity": 1,
                "unit_price": 79.99,
                "total_price": 79.99
            }
        ],
        "order_total": 395.97,
        "order_date": datetime(2024, 10, 22, 13, 45, 0),
        "delivery_date": datetime(2024, 10, 27, 15, 0, 0),
        "status": "processing"
    },
    {
        "order_number": "ORD-2024-008",
        "first_name": "Jennifer",
        "last_name": "Anderson",
        "user_email": "jennifer.anderson@example.com",
        "user_contact_number": "+1-555-0108",
        "items": [
            {
                "product_id": "PROD-015",
                "product_name": "Desk Lamp LED",
                "quantity": 1,
                "unit_price": 39.99,
                "total_price": 39.99
            },
            {
                "product_id": "PROD-016",
                "product_name": "Desk Organizer",
                "quantity": 1,
                "unit_price": 22.99,
                "total_price": 22.99
            }
        ],
        "order_total": 62.98,
        "order_date": datetime(2024, 10, 23, 16, 10, 0),
        "delivery_date": datetime(2024, 10, 28, 11, 0, 0),
        "status": "pending"
    },
    {
        "order_number": "ORD-2024-009",
        "first_name": "James",
        "last_name": "Thomas",
        "user_email": "james.thomas@example.com",
        "user_contact_number": "+1-555-0109",
        "items": [
            {
                "product_id": "PROD-017",
                "product_name": "Ergonomic Chair",
                "quantity": 1,
                "unit_price": 349.99,
                "total_price": 349.99
            }
        ],
        "order_total": 349.99,
        "order_date": datetime(2024, 10, 24, 10, 0, 0),
        "delivery_date": datetime(2024, 10, 30, 13, 0, 0),
        "status": "processing"
    },
    {
        "order_number": "ORD-2024-010",
        "first_name": "Amanda",
        "last_name": "White",
        "user_email": "amanda.white@example.com",
        "user_contact_number": "+1-555-0110",
        "items": [
            {
                "product_id": "PROD-018",
                "product_name": "Laptop Backpack",
                "quantity": 1,
                "unit_price": 54.99,
                "total_price": 54.99
            },
            {
                "product_id": "PROD-019",
                "product_name": "Water Bottle",
                "quantity": 1,
                "unit_price": 18.99,
                "total_price": 18.99
            },
            {
                "product_id": "PROD-002",
                "product_name": "USB-C Cable",
                "quantity": 3,
                "unit_price": 12.99,
                "total_price": 38.97
            }
        ],
        "order_total": 112.95,
        "order_date": datetime(2024, 10, 25, 12, 30, 0),
        "delivery_date": datetime(2024, 10, 29, 10, 0, 0),
        "status": "in_transit"
    }
]


# Order statuses for reference
ORDER_STATUSES = {
    "pending": "Order received, payment pending",
    "processing": "Payment confirmed, preparing for shipment",
    "in_transit": "Order shipped and on the way",
    "delivered": "Order successfully delivered",
    "cancelled": "Order cancelled by customer or system",
    "refunded": "Order refunded"
}


def get_orders():
    """
    Get all sample orders
    
    Returns:
        List of order dictionaries
    """
    return SAMPLE_ORDERS


def get_order_by_number(order_number: str):
    """
    Get a specific order by order number
    
    Args:
        order_number: The order number to search for
        
    Returns:
        Order dictionary or None if not found
    """
    return next((order for order in SAMPLE_ORDERS if order["order_number"] == order_number), None)


def get_orders_by_email(email: str):
    """
    Get all orders for a specific email address
    
    Args:
        email: The user email to search for
        
    Returns:
        List of order dictionaries
    """
    return [order for order in SAMPLE_ORDERS if order["user_email"] == email]


def get_orders_by_status(status: str):
    """
    Get all orders with a specific status
    
    Args:
        status: The order status to filter by
        
    Returns:
        List of order dictionaries
    """
    return [order for order in SAMPLE_ORDERS if order["status"] == status]
