from fastapi import FastAPI, HTTPException, Depends, status, Query, APIRouter, Header
from fastapi.security import HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from typing import List, Optional
from models.book_models import BookCreate, BookUpdate, BookInDB, BookResponse, BookDetailResponse, BookSearchRequest, BookSearchFilters, Quiz, Review, BookCategory, BookLanguage, BookAccessLevel, BookStatus
from database.connection import database, books_collection
from typing import Dict, Any
from utils.dependency import get_current_user, get_content_type, generate_unique_filename
from utils.token import  verify_access_token 
from datetime import datetime
from pydantic.json import pydantic_encoder
import json
# from botocore.client import Config
# from boto3 import client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
from utils.r2_utils import generate_get_url, generate_put_url
from utils.book_convertor import BookConvertor


router = APIRouter()



# s3 = client("s3", endpoint_url=os.environ["R2_ENDPOINT"],
#             aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
#             aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
#             config=Config(signature_version="s3v4"))


class BookService:
    @staticmethod
    async def create_book(book_data: BookCreate, created_by: str) -> BookInDB:
        book_dict = book_data.dict()
        book_dict = book_data.model_dump(mode="json")
        book_dict["created_by"] = created_by
        book_dict["created_at"] = datetime.utcnow()
        book_dict["updated_at"] = datetime.utcnow()
        
        if book_dict["status"] == BookStatus.PUBLISHED:
            book_dict["published_at"] = datetime.utcnow()        
        # book_dict = json.loads(json.dumps(book_data.dict(), default=pydantic_encoder))
        result = await books_collection.insert_one(book_dict)
        created_book = await books_collection.find_one({"_id": result.inserted_id})
        return BookInDB(**created_book)
    
    @staticmethod
    async def get_book_by_id(book_id: str) -> Optional[BookInDB]:
        try:
            book_data = await books_collection.find_one({"_id": ObjectId(book_id)})
            if book_data:
                return BookInDB(**book_data)
            return None
        except:
            return None
    
    @staticmethod
    async def get_books(
        skip: int = 0,
        limit: int = 20,
        filters: Optional[dict] = None
    ) -> List[BookInDB]:
        query = filters or {}
        cursor = books_collection.find(query).skip(skip).limit(limit)
        books = await cursor.to_list(length=limit)
        return [BookInDB(**book) for book in books]
    
    @staticmethod
    async def update_book(book_id: str, update_data: BookUpdate) -> BookInDB:
        # update_dict = update_data.dict(exclude_unset=True)
        # update_dict = update_data.model_dump(exclude_unset=True)
        update_dict = update_data.model_dump(mode="json")
        update_dict["updated_at"] = datetime.utcnow()
        
        await books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {"$set": update_dict}
        )
        
        updated_book = await books_collection.find_one({"_id": ObjectId(book_id)})
        if not updated_book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return BookInDB(**updated_book)
    
    @staticmethod
    async def search_books(search_request: BookSearchRequest) -> dict[str, any]:
        query = {}
        
        # Text search
        if search_request.query:
            query["$text"] = {"$search": search_request.query}
        
        # Apply filters
        filters = search_request.filters.dict(exclude_unset=True)
        
        if filters.get("categories"):
            query["categories"] = {"$in": filters["categories"]}
        
        if filters.get("languages"):
            query["language"] = {"$in": filters["languages"]}
        
        if filters.get("min_price") is not None or filters.get("max_price") is not None:
            price_query = {}
            if filters.get("min_price") is not None:
                price_query["$gte"] = filters["min_price"]
            if filters.get("max_price") is not None:
                price_query["$lte"] = filters["max_price"]
            query["price"] = price_query
        
        if filters.get("min_rating") is not None:
            query["average_rating"] = {"$gte": filters["min_rating"]}
        
        if filters.get("access_level"):
            query["access_level"] = filters["access_level"]
        
        if filters.get("has_quizzes") is not None:
            if filters["has_quizzes"]:
                query["quizzes.0"] = {"$exists": True}
            else:
                query["quizzes"] = {"$size": 0}
        
        if filters.get("is_free") is not None:
            query["is_free"] = filters["is_free"]
        
        # Get total count
        total = await books_collection.count_documents(query)
        
        # Apply sorting
        sort_order = -1 if search_request.sort_order == "desc" else 1
        sort_field = search_request.sort_by
        
        # Execute query
        cursor = books_collection.find(query).sort(sort_field, sort_order)
        cursor.skip((search_request.page - 1) * search_request.limit).limit(search_request.limit)
        
        books = await cursor.to_list(length=search_request.limit)
        
        return {
            "books": [BookInDB(**book) for book in books],
            "total": total,
            "page": search_request.page,
            "limit": search_request.limit,
            "has_next": (search_request.page * search_request.limit) < total
        }
    
    @staticmethod
    async def add_quiz_to_book(book_id: str, quiz_data: Quiz) -> BookInDB:
        quiz_dict = quiz_data.dict()
        
        await books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {
                "$push": {"quizzes": quiz_dict},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        updated_book = await books_collection.find_one({"_id": ObjectId(book_id)})
        if not updated_book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        return BookInDB(**updated_book)
    
    @staticmethod
    async def add_review_to_book(book_id: str, review_data: Review) -> BookInDB:
        review_dict = review_data.dict()
        
        # Update book ratings
        book = await books_collection.find_one({"_id": ObjectId(book_id)})
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        new_total_ratings = book.get("total_ratings", 0) + 1
        new_average_rating = (
            (book.get("average_rating", 0) * book.get("total_ratings", 0)) + review_data.rating
        ) / new_total_ratings
        
        await books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {
                "$push": {"reviews": review_dict},
                "$set": {
                    "total_ratings": new_total_ratings,
                    "average_rating": round(new_average_rating, 2),
                    "total_reviews": book.get("total_reviews", 0) + 1,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        updated_book = await books_collection.find_one({"_id": ObjectId(book_id)})
        return BookInDB(**updated_book)
    
    @staticmethod
    async def increment_book_stats(book_id: str, field: str, value: int = 1) -> None:
        await books_collection.update_one(
            {"_id": ObjectId(book_id)},
            {
                "$inc": {field: value},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

# Helper functions
def book_in_db_to_response(book: BookInDB, include_content: bool = False) -> BookResponse:
    base_data = {
        "id": str(book.id),
        "title": book.title,
        "subtitle": book.subtitle,
        "author": book.author,
        "description": book.description,
        "categories": book.categories,
        "language": book.language,
        "cover_image_url": str(book.cover_image_url),
        "price": book.price,
        "discount_price": book.discount_price,
        "is_free": book.is_free,
        "total_pages": book.total_pages,
        "average_rating": book.average_rating,
        "total_ratings": book.total_ratings,
        "total_reviews": book.total_reviews,
        "access_level": book.access_level,
        "status": book.status,
        "publication_date": book.publication_date,
        "estimated_reading_time": book.estimated_reading_time,
        "has_quizzes": len(book.quizzes) > 0,
        "active_quizzes": len([q for q in book.quizzes if q.is_active])
    }
    
    if include_content:
        return BookDetailResponse(
            **base_data,
            long_description=book.long_description,
            chapters=book.chapters,
            quizzes=book.quizzes,
            reviews=book.reviews,
            co_authors=book.co_authors,
            publisher=book.publisher,
            isbn=book.isbn,
            tags=book.tags,
            book_content_url=str(book.book_content_url) if include_content else None,
            sample_chapter_url=str(book.sample_chapter_url) if book.sample_chapter_url else None,
            word_count=book.word_count,
            edition=book.edition,
            difficulty_level=book.difficulty_level,
            total_purchases=book.total_purchases,
            total_reads=book.total_reads
        )
    
    return BookResponse(**base_data)

# FastAPI Routes
@router.post("/books-create/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate, Authorization:str = Header(str) ):
    if not Authorization:
        raise HTTPException(status_code=400,detail='bad request')
    
    try:
        sign, token = Authorization.split()
        if sign.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid token type")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Authorization format")
        
    data =  verify_access_token(token);
    book = await BookService.create_book(book_data, data['user_id'])
    
    #   start 2 back background  process
    # 1. file ko convert karo 
    # case 1: docx
         # convert to epub
         # convert to pdf
    # case 2: epub
        # convert to pdf
    # case 3 : pdf
         # convert to epub         
    # 2. extract toc or chapter from pdf
    # start process run BookConvertor
    BookConvertor(book);
    return book_in_db_to_response(book)
  



@router.get("/books/", response_model=Dict[str, Any])
async def get_books(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[BookCategory] = None,
    language: Optional[BookLanguage] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    access_level: Optional[BookAccessLevel] = None
):
    filters = BookSearchFilters(
        categories=[category] if category else None,
        languages=[language] if language else None,
        min_price=min_price,
        max_price=max_price,
        access_level=access_level
    )
    
    search_request = BookSearchRequest(
        page=page,
        limit=limit,
        filters=filters
    )
    
    # url = book.cover_image_url
    # path = urlparse(url).path
    # filename = os.path.basename(path)
    # print("filename",filename)
    # signed_url = await generate_get_url(f"images/{filename}")
    # print('signed_url',signed_url)
    # book.cover_image_url=signed_url
    
    print('inside fetch book functions', search_request)
    result = await BookService.search_books(search_request)
    
    for book in result["books"]:
        if not book.cover_image_url:
            continue  # skip missing images
        url = str(book.cover_image_url)
        path = urlparse(url).path
        filename = os.path.basename(path)
        # print("filename",filename)
        signed_url =  generate_get_url(f"images/{filename}")
        # print('signed_url',signed_url)
        book.cover_image_url=signed_url
        url=str(book.book_content_url)
        path = urlparse(url).path
        filename=os.path.basename(path)
        signed_url=generate_get_url(f"documents/{filename}")
        book.book_content_url=signed_url
    
    
    return {
        "books": [book_in_db_to_response(book) for book in result["books"]],
        "total": result["total"],
        "page": result["page"],
        "limit": result["limit"],
        "has_next": result["has_next"]
    }




@router.get("/books/{book_id}", response_model=BookDetailResponse)
async def get_book(book_id: str,  Authorization:str = Header(str)):
    book = await BookService.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if not Authorization:
        raise HTTPException(status_code=400,detail='bad request')
    
    try:
        sign, token = Authorization.split()
        if sign.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid token type")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Authorization format")
        
    user =  verify_access_token(token);
    
    def check_user_book_access(user_id: str, book_id: str) -> bool:
        # Placeholder function to check if user has purchased or has access to the book
        # In real implementation, check user's purchases or subscriptions
        return True  # Defaulting to False for demonstration purposes
    
    # Check if user has access to full content
    has_access = (
        book.is_free or 
        book.access_level == BookAccessLevel.FREE or
        check_user_book_access(user["user_id"], book_id)
    )
    
    url = str(book.cover_image_url)
    path = urlparse(url).path
    filename = os.path.basename(path)
    # print("filename",filename)
    signed_url =  generate_get_url(f"images/{filename}")
    # print('signed_url',signed_url)
    book.cover_image_url=signed_url
    url=str(book.book_content_url)
    path = urlparse(url).path
    filename=os.path.basename(path)
    signed_url=generate_get_url(f"documents/{filename}")
    book.book_content_url=signed_url
   
    
    
    return book_in_db_to_response(book, include_content=has_access)

@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: str, update_data: BookUpdate, Authorization: str = Header(str)):
    book = await BookService.update_book(book_id, update_data)
    return book_in_db_to_response(book)


@router.post("/books/{book_id}/quizzes", response_model=BookDetailResponse)
async def add_quiz_to_book(book_id: str, quiz_data: Quiz, user: Dict = Depends(get_current_user)):
    book = await BookService.add_quiz_to_book(book_id, quiz_data)
    return book_in_db_to_response(book, include_content=True)

@router.post("/books/{book_id}/reviews", response_model=BookDetailResponse)
async def add_review(book_id: str, review_data: Review, user: Dict = Depends(get_current_user)):
    book = await BookService.add_review_to_book(book_id, review_data)
    return book_in_db_to_response(book, include_content=True)

@router.post("/books/{book_id}/increment-reads")
async def increment_reads(book_id: str):
    await BookService.increment_book_stats(book_id, "total_reads")
    return {"message": "Read count updated"}

@router.post("/books/{book_id}/increment-purchases")
async def increment_purchases(book_id: str):
    await BookService.increment_book_stats(book_id, "total_purchases")
    return {"message": "Purchase count updated"}


@router.delete("/books/{book_id}", status_code=status.HTTP_200_OK)
async def delete_book(book_id: str, Authorization: str = Header(None)):
    if not Authorization:
        raise HTTPException(status_code=400, detail="Authorization header missing")

    try:
        sign, token = Authorization.split()
        if sign.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid token type")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Authorization format")

    # Verify JWT token
    data = verify_access_token(token)

    # Delete the book if it belongs to the user
    book = await books_collection.find_one_and_delete({
        "created_by": data["user_id"],
        "_id": ObjectId(book_id)
    })

    if not book:
        raise HTTPException(status_code=404, detail="Book not found or unauthorized")

    return {"message": "Book deleted successfully", "book_id": str(book_id)}
    

# for generate presign url for upload image and content of ebook
# Request model for validation
class UploadRequest(BaseModel):
    filename: str
    file_type: str = "image"  # can be "image", "document", etc.


@router.post("/get-upload-url")
def get_upload_url(request: UploadRequest):
    filename = request.filename
    file_type = request.file_type
    
    # Validate file type
    if file_type == "image":
        allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'ico'}
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid image format. Allowed: {', '.join(allowed_extensions)}"
            )
            
    if file_type == "document":
        allowed_extensions = {'pdf', 'doc', 'docx', 'epub'}
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid document format. Allowed: {', '.join(allowed_extensions)}"
            )
    
    content_type = get_content_type(filename, file_type)
    
    # Use different folders based on file type
    folder = "images" if file_type == "image" else "documents"
    key = f"{folder}/{generate_unique_filename(filename)}"
    
    # url = s3.generate_presigned_url(
    #     ClientMethod="put_object",
    #     Params={
    #         "Bucket": os.environ["R2_BUCKET"], 
    #         "Key": key, 
    #         "ContentType": content_type
    #     },
    #     ExpiresIn=3600
    # )
    
    url = generate_put_url(key=key, content_type=content_type)
    
    fileUrl= f"{os.environ['R2_ENDPOINT']}/{os.environ['R2_BUCKET']}/{key}"
    
    return {
        "upload_url": url, 
        "key": key, 
        "fileUrl":fileUrl,
        "content_type": content_type,
        "expires_in": 3600
    }




@router.on_event("startup")
async def create_indexes():
    # Drop old text index if exists
    try:
        await books_collection.drop_index("title_text_description_text_author_text")
    except Exception:
        pass

    # Create proper text index for title/description/author search
    await books_collection.create_index(
        [("title", "text"), ("description", "text"), ("author", "text")],
        name="books_text_search",
        default_language="none",
        language_override="none"
    )

    # Add simple indexes for filtering/sorting
    await books_collection.create_index([("categories", 1)])
    await books_collection.create_index([("language", 1)])  # ✅ language filter
    await books_collection.create_index([("price", 1)])
    await books_collection.create_index([("average_rating", -1)])
    await books_collection.create_index([("publication_date", -1)])
    await books_collection.create_index([("created_at", -1)])
    await books_collection.create_index([("status", 1)])
    await books_collection.create_index([("access_level", 1)])

    # print("Book indexes created successfully")
