from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "readbucks_db")

async_client = AsyncIOMotorClient(MONGODB_URL)
database = async_client[DATABASE_NAME]


async def check_connection():
    try:
        await async_client.admin.command('ping')
        print("✅ MongoDB se connection successful!")
        return True
    except ConnectionFailure:
        print("❌ MongoDB connection failed!")
        return False