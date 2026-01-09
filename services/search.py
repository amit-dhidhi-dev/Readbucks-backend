# backend/main.py
from fastapi import APIRouter, HTTPException, Query, Depends
from database.connection import books_collection
from typing import List, Optional, Union
from datetime import datetime
from bson import ObjectId
import re

router = APIRouter()


# Search Books API - Aapke data ke according
@router.get("/api/books/search")
async def search_books(
    q: Optional[str] = Query(None, min_length=1),
    category: Optional[str] = None,
    author: Optional[str] = None,
    language: Optional[str] = None,
    access_level: Optional[str] = None,
    status: Optional[str] = None,
    is_free: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    difficulty_level: Optional[str] = None,
    tags: Optional[str] = None,
    sort_by: str = "relevance",
    page: int = 1,
    limit: int = 12
):
    # Build search query
    query = {}
    
    # Text search on multiple fields
    if q:
        # Case-insensitive regex search
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"subtitle": {"$regex": q, "$options": "i"}},
            {"author": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"long_description": {"$regex": q, "$options": "i"}},
            {"publisher": {"$regex": q, "$options": "i"}},
            {"categories": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}}
        ]
    
    # Filter by category (categories array me search)
    if category:
        query["categories"] = {"$regex": category, "$options": "i"}
    
    # Other filters
    if author:
        query["author"] = {"$regex": author, "$options": "i"}
    
    if language:
        query["language"] = {"$regex": language, "$options": "i"}
    
    if access_level:
        query["access_level"] = access_level
    
    if status:
        query["status"] = status
    
    if is_free is not None:
        query["is_free"] = is_free
    
    if difficulty_level:
        query["difficulty_level"] = difficulty_level
    
    if tags:
        # Multiple tags ko comma separated handle karna
        tag_list = [tag.strip() for tag in tags.split(",")]
        query["tags"] = {"$in": tag_list}
    
    # Price filter
    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = min_price
        if max_price is not None:
            query["price"]["$lte"] = max_price
    
    # Pagination
    skip = (page - 1) * limit
    
    # Sorting
    sort_options = {
        "relevance": [("created_at", -1)],  # Default: newest first
        "newest": [("created_at", -1)],
        "oldest": [("created_at", 1)],
        "price_low": [("price", 1)],
        "price_high": [("price", -1)],
        "title_asc": [("title", 1)],
        "title_desc": [("title", -1)],
        "popular": [("word_count", -1)]  # Example: word count se popularity assume
    }
    
    sort_criteria = sort_options.get(sort_by, sort_options["relevance"])
    
    # Get total count
    total = await books_collection.count_documents(query)
    
    # Execute search
    books_cursor = books_collection.find(query).sort(sort_criteria).skip(skip).limit(limit)
    books = await books_cursor.to_list(length=limit)
    
    # Convert ObjectId to string
    for book in books:
        book["_id"] = str(book["_id"])
        book["created_by"] = str(book["created_by"]) if book.get("created_by") else None
    
    return {
        "books": books,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

# Auto-suggest API
@router.get("/api/books/autocomplete")
async def autocomplete(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=20)
):
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"title": {"$regex": f"^{re.escape(q)}", "$options": "i"}},
                    {"author": {"$regex": f"^{re.escape(q)}", "$options": "i"}},
                    {"subtitle": {"$regex": f"^{re.escape(q)}", "$options": "i"}},
                    {"categories": {"$regex": f"^{re.escape(q)}", "$options": "i"}}
                ],
                "status": {"$ne": "archived"}  # Archived books ko exclude
            }
        },
        {"$limit": limit},
        {
            "$project": {
                "_id": 1,
                "title": 1,
                "subtitle": 1,
                "author": 1,
                "price": 1,
                "is_free": 1,
                "categories": 1,
                "cover_image_url": 1,
                "language": 1
            }
        }
    ]
    
    suggestions = await books_collection.aggregate(pipeline).to_list(length=limit)
    
    # Convert ObjectId to string
    for suggestion in suggestions:
        suggestion["_id"] = str(suggestion["_id"])
    
    return suggestions

# Get all unique categories
@router.get("/api/books/categories")
async def get_all_categories():
    pipeline = [
        {"$match": {"categories": {"$exists": True, "$ne": []}}},
        {"$unwind": "$categories"},
        {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    categories = await books_collection.aggregate(pipeline).to_list(length=100)
    return {"categories": categories}

# Get all languages
@router.get("/api/books/languages")
async def get_all_languages():
    languages = await books_collection.distinct("language")
    return {"languages": [lang.capitalize() for lang in languages if lang]}

# Get all tags
@router.get("/api/books/tags")
async def get_all_tags():
    pipeline = [
        {"$match": {"tags": {"$exists": True, "$ne": []}}},
        {"$unwind": "$tags"},
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 50}
    ]
    
    tags = await books_collection.aggregate(pipeline).to_list(length=50)
    return {"tags": tags}

# Get search filters metadata
@router.get("/api/books/search-filters")
async def get_search_filters():
    """Get all available filters for search page"""
    pipeline = [
        {
            "$facet": {
                "price_range": [
                    {
                        "$group": {
                            "_id": None,
                            "min_price": {"$min": "$price"},
                            "max_price": {"$max": "$price"},
                            "avg_price": {"$avg": "$price"}
                        }
                    }
                ],
                "difficulty_levels": [
                    {"$match": {"difficulty_level": {"$exists": True}}},
                    {"$group": {"_id": "$difficulty_level", "count": {"$sum": 1}}}
                ],
                "access_levels": [
                    {"$group": {"_id": "$access_level", "count": {"$sum": 1}}}
                ],
                "statuses": [
                    {"$group": {"_id": "$status", "count": {"$sum": 1}}}
                ],
                "languages": [
                    {"$group": {"_id": "$language", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 10}
                ]
            }
        }
    ]
    
    filters_data = await books_collection.aggregate(pipeline).to_list(length=1)
    return filters_data[0] if filters_data else {}

# Book detail by ID
@router.get("/api/books/{book_id}")
async def get_book_detail(book_id: str):
    try:
        book = await books_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        # Convert ObjectId to string
        book["_id"] = str(book["_id"])
        book["created_by"] = str(book["created_by"]) if book.get("created_by") else None
        
        return book
    except:
        raise HTTPException(status_code=400, detail="Invalid book ID")