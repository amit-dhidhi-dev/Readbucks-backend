from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pymongo.errors import ConnectionFailure


load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "readbucks_db")

async_client = AsyncIOMotorClient(MONGODB_URL)
database = async_client[DATABASE_NAME]
books_collection = database["books"]
users_collection  = database["users"]



async def check_connection():
    try:
        await async_client.admin.command('ping')       
        print("✅ MongoDB se connection successful!")
        return True
    except ConnectionFailure:
        print("❌ MongoDB connection failed!")
        return False
    

async def create_search_indexes():
    """
    MongoDB me search ke liye indexes create karte hain.
    Ye indexes fast search ke liye zaroori hain.
    """
    try:
        # Text search index for full-text search
        text_index_fields = [
            ("title", "text"),
            ("subtitle", "text"),
            ("author", "text"),
            ("description", "text"),
            ("long_description", "text"),
            ("categories", "text"),
            ("tags", "text"),
            ("publisher", "text")
        ]
        
        # Check if text index already exists
        existing_indexes = await books_collection.index_information()
        
        if "title_text_subtitle_text_author_text_description_text_long_description_text_categories_text_tags_text_publisher_text" not in existing_indexes:
            await books_collection.create_index(
                text_index_fields,
                name="book_full_text_search_index",
                default_language="english",
                weights={
                    "title": 10,
                    "author": 8,
                    "categories": 6,
                    "subtitle": 5,
                    "description": 4,
                    "long_description": 3,
                    "tags": 2,
                    "publisher": 2
                }
            )
            print("✅ Full-text search index created successfully!")
        else:
            print("ℹ️  Full-text search index already exists!")

        # Single field indexes for faster filtering
        indexes_to_create = [
            # For category filtering
            [("categories", 1), {"name": "categories_index"}],
            
            # For author search
            [("author", 1), {"name": "author_index"}],
            
            # For language filtering
            [("language", 1), {"name": "language_index"}],
            
            # For access level filtering
            [("access_level", 1), {"name": "access_level_index"}],
            
            # For status filtering
            [("status", 1), {"name": "status_index"}],
            
            # For free/paid filtering
            [("is_free", 1), {"name": "is_free_index"}],
            
            # For price range filtering and sorting
            [("price", 1), {"name": "price_asc_index"}],
            [("price", -1), {"name": "price_desc_index"}],
            
            # For difficulty level filtering
            [("difficulty_level", 1), {"name": "difficulty_level_index"}],
            
            # For publication date sorting
            [("publication_date", -1), {"name": "publication_date_desc_index"}],
            [("publication_date", 1), {"name": "publication_date_asc_index"}],
            
            # For created/updated date sorting
            [("created_at", -1), {"name": "created_at_desc_index"}],
            [("updated_at", -1), {"name": "updated_at_desc_index"}],
            
            # For ISBN search (unique index if needed)
            [("isbn", 1), {"name": "isbn_index", "sparse": True}],
            
            # For publisher search
            [("publisher", 1), {"name": "publisher_index"}],
            
            # For total pages filtering
            [("total_pages", 1), {"name": "total_pages_index"}],
            
            # For word count filtering
            [("word_count", 1), {"name": "word_count_index"}],
            
            # For estimated reading time
            [("estimated_reading_time", 1), {"name": "reading_time_index"}],
            
            # For edition filtering
            [("edition", 1), {"name": "edition_index"}],
            
            # Compound index for common queries
            [("categories", 1), ("price", 1), {"name": "category_price_index"}],
            [("author", 1), ("created_at", -1), {"name": "author_recent_index"}],
            [("is_free", 1), ("categories", 1), {"name": "free_category_index"}]
        ]

        created_count = 0
        for index_spec in indexes_to_create:
            if len(index_spec) == 2 and isinstance(index_spec[1], dict):
                # Compound index with options
                fields = index_spec[0]
                options = index_spec[1]
                index_name = options.get("name", "")
            else:
                # Simple index
                fields = index_spec[0]
                options = {"name": f"{fields[0]}_index"}
            
            # Check if index already exists
            if index_name not in existing_indexes:
                try:
                    if isinstance(fields, list):
                        # Compound index
                        await books_collection.create_index(fields, **options)
                    else:
                        # Single field index
                        await books_collection.create_index([fields], **options)
                    print(f"✅ Index '{index_name}' created successfully!")
                    created_count += 1
                except Exception as e:
                    print(f"⚠️  Error creating index '{index_name}': {e}")
            else:
                print(f"ℹ️  Index '{index_name}' already exists!")

        if created_count == 0:
            print("✅ All indexes are already up to date!")
        else:
            print(f"✅ Total {created_count} new indexes created successfully!")

        return True

    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        return False


async def check_and_create_indexes():
    """
    Connection check karo aur agar zaroori ho to indexes create karo.
    """
    is_connected = await check_connection()
    
    if is_connected:
        print("🔍 Checking and creating indexes...")
        await create_search_indexes()
        return True
    return False


# Helper function to get index information
async def get_index_info():
    """
    Existing indexes ki information get karo.
    """
    try:
        indexes = await books_collection.index_information()
        print("\n📊 Existing Indexes:")
        print("-" * 50)
        for name, info in indexes.items():
            print(f"Name: {name}")
            print(f"  Fields: {info.get('key', [])}")
            print(f"  Unique: {info.get('unique', False)}")
            print(f"  Sparse: {info.get('sparse', False)}")
            print("-" * 50)
        return indexes
    except Exception as e:
        print(f"❌ Error getting index info: {e}")
        return None


# Helper function to drop all indexes (development use only)
async def drop_all_indexes():
    """
    Sabhi indexes drop karo (development/testing ke liye).
    WARNING: Production me use mat karo!
    """
    try:
        # Keep only the default _id index
        result = await books_collection.drop_indexes()
        print(f"✅ All indexes dropped successfully!")
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Error dropping indexes: {e}")
        return False


# Helper function to optimize search performance
async def optimize_search_performance():
    """
    Search performance optimize karne ke liye additional settings.
    """
    try:
        # Get collection stats
        stats = await database.command("collstats", "books")
        
        print("\n📈 Collection Statistics:")
        print(f"  Total documents: {stats.get('count', 0)}")
        print(f"  Size on disk: {stats.get('size', 0) / (1024*1024):.2f} MB")
        print(f"  Total index size: {stats.get('totalIndexSize', 0) / (1024*1024):.2f} MB")
        
        # Create wildcard index for tags array if frequently searched
        existing_indexes = await books_collection.index_information()
        
        if "tags_wildcard_index" not in existing_indexes:
            await books_collection.create_index(
                [("tags.$**", 1)],
                name="tags_wildcard_index"
            )
            print("✅ Wildcard index for tags created!")
        
        # Create index for case-insensitive author search
        if "author_ci_index" not in existing_indexes:
            await books_collection.create_index(
                [("author", "text")],
                name="author_ci_index",
                default_language="english",
                collation={"locale": "en", "strength": 2}  # Case-insensitive
            )
            print("✅ Case-insensitive author index created!")
        
        print("✅ Search performance optimization completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error optimizing search performance: {e}")
        return False


# Async context manager for better resource management
class MongoDBConnection:
    def __init__(self):
        self.client = None
        self.db = None
    
    async def __aenter__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        await check_connection()
        return self.db
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()


# Main execution for testing
async def main():
    """
    Test function to run connection and index creation.
    """
    print("🔧 MongoDB Connection and Index Setup")
    print("=" * 50)
    
    # Check connection
    connected = await check_connection()
    if not connected:
        print("❌ Cannot proceed without MongoDB connection!")
        return
    
    # Create indexes
    await create_search_indexes()
    
    # Get index info
    await get_index_info()
    
    # Optimize performance (optional)
    # await optimize_search_performance()
    
    print("\n✅ Setup completed successfully!")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())