"""
Database connection and utilities
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from langgraph.checkpoint.mongodb import MongoDBSaver
from app.core.config import settings
from app.fixtures.orders import SAMPLE_ORDERS


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None
    checkpointer: MongoDBSaver = None  # Global checkpointer instance


db = Database()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency to get database instance
    """
    return db.db


def get_checkpointer() -> MongoDBSaver:
    """
    Get the global checkpointer instance
    """
    return db.checkpointer


async def load_sample_data():
    """
    Load sample orders into database (for development/testing)
    Only loads if orders collection is empty
    """
    try:
        # Check if orders collection already has data
        count = await db.db.orders.count_documents({})
        print(f"[DATABASE] Orders collection currently has {count} documents")
        
        if count == 0:
            # Insert sample orders
            result = await db.db.orders.insert_many(SAMPLE_ORDERS)
            print(f"✅ Loaded {len(SAMPLE_ORDERS)} sample orders into database")
            print(f"[DATABASE] Inserted order IDs: {result.inserted_ids[:3]}... (showing first 3)")
            
            # Verify by checking a sample order
            sample = await db.db.orders.find_one({"order_number": "ORD-2024-001"})
            if sample:
                print(f"[DATABASE] ✅ Verification: Found order ORD-2024-001 for {sample.get('first_name')} {sample.get('last_name')}")
            else:
                print(f"[DATABASE] ⚠️  Verification failed: Could not find ORD-2024-001")
        else:
            print(f"ℹ️  Database already has {count} orders, skipping sample data load")
            # Still verify we can read an order
            sample = await db.db.orders.find_one({})
            if sample:
                print(f"[DATABASE] Sample order from DB: {sample.get('order_number', 'unknown')}")
    except Exception as e:
        print(f"⚠️  Error loading sample data: {e}")
        import traceback
        traceback.print_exc()


async def connect_to_mongo():
    """
    Create database connection, checkpointer, and load sample data
    """
    # Async client for database operations
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.db = db.client[settings.mongodb_db_name]
    print(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")
    
    # Sync client for checkpointer (LangGraph requirement)
    print(f"[DATABASE] Creating global checkpointer instance")
    sync_client = MongoClient(settings.mongodb_url)
    db.checkpointer = MongoDBSaver(sync_client, settings.mongodb_db_name, "checkpoints")
    print(f"✅ Checkpointer initialized")
    
    # Load sample data on startup
    await load_sample_data()


async def close_mongo_connection():
    """
    Close database connection
    """
    db.client.close()
    print("✅ Closed MongoDB connection")
