# MongoDB Fixtures

This directory contains sample data fixtures for development and testing.

## Sample Orders

The `orders.py` file contains 10 sample customer orders with the following structure:

### Order Fields
- **order_number**: Unique order identifier (e.g., "ORD-2024-001")
- **user_email**: Customer email address
- **user_contact_number**: Customer phone number
- **items**: List of ordered items with:
  - product_id
  - product_name
  - quantity
  - unit_price
  - total_price
- **order_total**: Total order amount
- **order_date**: When the order was placed
- **delivery_date**: Expected/actual delivery date
- **status**: Order status (pending, processing, in_transit, delivered, cancelled, refunded)

## Loading Fixtures

### Prerequisites
1. Ensure MongoDB is running:
   ```bash
   # Local MongoDB
   # or
   # Docker
   docker-compose up -d mongodb
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

### Load Data

#### Option 1: From your local machine (Recommended)
```bash
# Make sure MongoDB is running (via Docker)
docker-compose up -d mongodb

# Run the fixture loader script
python scripts/load_fixtures.py
```

#### Option 2: From within Docker container
```bash
# Access the web container
docker-compose exec web bash

# Run the script inside the container
python scripts/load_fixtures.py
```

This will:
1. Clear existing orders in the database
2. Insert 10 sample orders
3. Create indexes on key fields (order_number, user_email, status, order_date)
4. Display a summary of loaded data

## Using Fixtures in Code

```python
from app.fixtures.orders import (
    SAMPLE_ORDERS,
    get_orders,
    get_order_by_number,
    get_orders_by_email,
    get_orders_by_status
)

# Get all orders
all_orders = get_orders()

# Get specific order
order = get_order_by_number("ORD-2024-001")

# Get orders by email
user_orders = get_orders_by_email("john.smith@example.com")

# Get orders by status
processing_orders = get_orders_by_status("processing")
```

## Order Statuses

- **pending**: Order received, payment pending
- **processing**: Payment confirmed, preparing for shipment
- **in_transit**: Order shipped and on the way
- **delivered**: Order successfully delivered
- **cancelled**: Order cancelled by customer or system
- **refunded**: Order refunded

## Sample Data Overview

- 10 orders from different customers
- Various order statuses (delivered, in_transit, processing, pending)
- Order dates spanning October 2024
- Different product combinations
- Total order value: ~$1,650

## Querying in MongoDB Shell

```javascript
// Connect to MongoDB
mongosh chatbot

// Find all orders
db.orders.find()

// Find order by number
db.orders.findOne({order_number: "ORD-2024-001"})

// Find orders by email
db.orders.find({user_email: "john.smith@example.com"})

// Find orders by status
db.orders.find({status: "in_transit"})

// Count orders by status
db.orders.aggregate([
  {$group: {_id: "$status", count: {$sum: 1}}}
])
```

## Using with Mongo Express

1. Start Mongo Express:
   ```bash
   docker-compose up -d mongo-express
   ```

2. Open http://localhost:8081
3. Login: admin/admin123
4. Navigate to: chatbot → orders

## Adding More Fixtures

To add more sample data:

1. Edit `app/fixtures/orders.py`
2. Add new order dictionaries to the `SAMPLE_ORDERS` list
3. Run the loader script again
