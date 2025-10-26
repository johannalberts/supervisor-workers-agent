"""
Load sample data fixtures into MongoDB
Run this script to populate the database with sample orders
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.fixtures.orders import SAMPLE_ORDERS


async def load_fixtures():
    """
    Load sample orders into MongoDB
    """
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    try:
        # Clear existing orders (optional - comment out to keep existing data)
        print("Clearing existing orders...")
        await db.orders.delete_many({})
        
        # Insert sample orders
        print(f"Loading {len(SAMPLE_ORDERS)} sample orders...")
        result = await db.orders.insert_many(SAMPLE_ORDERS)
        
        print(f"✅ Successfully inserted {len(result.inserted_ids)} orders")
        
        # Create indexes for better query performance
        print("Creating indexes...")
        await db.orders.create_index("order_number", unique=True)
        await db.orders.create_index("user_email")
        await db.orders.create_index("status")
        await db.orders.create_index("order_date")
        
        print("✅ Indexes created")
        
        # Display summary
        print("\n📊 Order Summary:")
        statuses = await db.orders.aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        for status_doc in statuses:
            print(f"  - {status_doc['_id']}: {status_doc['count']} orders")
        
        total_value = sum(order["order_total"] for order in SAMPLE_ORDERS)
        print(f"\n💰 Total order value: ${total_value:.2f}")
        
    except Exception as e:
        print(f"❌ Error loading fixtures: {e}")
        raise
    finally:
        client.close()
        print("\n✅ Database connection closed")


if __name__ == "__main__":
    print("🔄 Loading MongoDB fixtures...")
    asyncio.run(load_fixtures())
