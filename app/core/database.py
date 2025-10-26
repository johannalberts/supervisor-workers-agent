"""
Database connection and utilities
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings


class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None


db = Database()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency to get database instance
    """
    return db.db


async def connect_to_mongo():
    """
    Create database connection
    """
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.db = db.client[settings.mongodb_db_name]
    print(f"✅ Connected to MongoDB: {settings.mongodb_db_name}")


async def close_mongo_connection():
    """
    Close database connection
    """
    db.client.close()
    print("✅ Closed MongoDB connection")
