from fastapi import APIRouter, HTTPException, status, Query
from database.connection import database, users_collection
from bson import ObjectId
from typing import List


from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pymongo import MongoClient
from pymongo.collection import Collection
import os
from typing import List
from models.user_models import (
    UserCreate,
    UserInDB,
    UserResponse,
    UserStatsResponse,
    SocialAuthProvider,
    UserUpdate,
    QuizParticipation,
    ReadingProgress,
)
from database.connection import database, users_collection, books_collection
from datetime import datetime
from typing import Optional
from bson import ObjectId
from utils.token import (
    verify_access_token,
    create_access_token,
    hash_password,
    verify_password,
)


security = HTTPBearer()


router = APIRouter()


class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> UserInDB:
        # Check if user already exists with same social auth
        existing_user = await users_collection.find_one(
            {
                "social_auth.provider": user_data.social_auth.provider,
                "social_auth.provider_user_id": user_data.social_auth.provider_user_id,
            }
        )

        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

        # print("Creating user with data:", user_data)
        user_dict = user_data.dict()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["last_login"] = datetime.utcnow()

        result = await users_collection.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        user_dict["social_auth"] = [user_dict["social_auth"]]

        return UserInDB(**user_dict)

    @staticmethod
    async def get_user_by_id(user_id: str):
        user_data = await users_collection.find_one({"_id": ObjectId(user_id)})

        if user_data and isinstance(user_data.get("_id"), ObjectId):
            user_data["_id"] = str(user_data["_id"])
        if user_data:
            # print("User data found:", UserInDB(**user_data))
            # return UserInDB(**user_data)
            return user_data
        return None

    @staticmethod
    async def get_user_by_social_auth(
        provider: SocialAuthProvider, provider_user_id: str
    ) -> Optional[UserInDB]:
        user_data = await users_collection.find_one(
            {
                "social_auth.provider": provider,
                "social_auth.provider_user_id": provider_user_id,
            }
        )
        if user_data:
            return UserInDB(**user_data)
        return None

    @staticmethod
    async def update_user(user_id: str, update_data: UserUpdate) -> UserInDB:
        update_dict = update_data.dict(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()

        await users_collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": update_dict}
        )

        return await UserService.get_user_by_id(user_id)

    @staticmethod
    async def add_quiz_participation(
        user_id: str, quiz_data: QuizParticipation
    ) -> UserInDB:
        quiz_dict = quiz_data.dict()

        update_data = {
            "$push": {"quiz_participations": quiz_dict},
            "$set": {"updated_at": datetime.utcnow()},
        }

        if quiz_data.is_winner:
            update_data["$inc"] = {
                "total_quiz_wins": 1,
                "total_prize_money": quiz_data.prize_amount,
            }

        await users_collection.update_one({"_id": ObjectId(user_id)}, update_data)

        return await UserService.get_user_by_id(user_id)

    @staticmethod
    async def update_reading_progress(
        user_id: str, progress_data: ReadingProgress
    ) -> UserInDB:
        # Remove existing progress for this book
        users_collection.update_one(
            {"_id": user_id},
            {"$pull": {"reading_progress": {"book_id": progress_data.book_id}}},
        )

        # Add new progress
        progress_dict = progress_data.dict()
        users_collection.update_one(
            {"_id": user_id},
            {
                "$push": {"reading_progress": progress_dict},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )

        return await UserService.get_user_by_id(user_id)


# FastAPI Routes
@router.post("/users/", response_model=UserResponse)
async def create_user(user_data: UserCreate):
    return await UserService.create_user(user_data)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    user = await UserService.get_user_by_id(user_id)
    print("Fetched user:", user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/getCurrentUser")
async def get_current_user(token: str):
    payload = verify_access_token(token)
    # print("payload", payload["user_id"])
    user = await UserService.get_user_by_id(payload["user_id"])
    # print("Fetched user:", user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, update_data: UserUpdate):
    return await UserService.update_user(user_id, update_data)


@router.post("/users/{user_id}/quiz-participation")
async def add_quiz_participation(user_id: str, quiz_data: QuizParticipation):
    return await UserService.add_quiz_participation(user_id, quiz_data)


@router.post("/users/{user_id}/reading-progress")
async def update_reading_progress(user_id: str, progress_data: ReadingProgress):
    return await UserService.update_reading_progress(user_id, progress_data)


@router.get("/users/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(user_id: str):
    user = await UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Calculate stats
    total_quizzes = len(user.quiz_participations)
    avg_score = (
        sum([q.score for q in user.quiz_participations]) / total_quizzes
        if total_quizzes > 0
        else 0
    )

    return UserStatsResponse(
        user_id=user_id,
        total_quizzes_taken=total_quizzes,
        average_quiz_score=avg_score,
        favorite_genres=[],  # You can implement genre tracking
        reading_streak=0,  # Implement streak logic
        monthly_reading_goal=user.reading_goals.get("monthly", 0),
        monthly_reading_progress=user.reading_goals.get("monthly_progress", 0),
    )


# routes/user_routes.py
# @router.post("/users/library")
# async def add_book_to_library(token: str, book_data: dict = None):
#     try:
#         # Validate token
#         payload = verify_access_token(token)
#         user_id = payload["user_id"]

#         # Get user
#         user = await UserService.get_user_by_id(user_id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         # print('in my library section', user)

#         # Validate book_data
#         if not book_data:
#             raise HTTPException(status_code=400, detail="Book data is required")

#         # Create book dictionary with default values
#         book_dict = {
#             "book_ids": str(book_data.get("book_id", "")),  # Ensure string
#             "book_name": book_data.get("book_name", ""),
#             "book_author": book_data.get("book_author", ""),
#             "book_cover": book_data.get("book_cover", ""),
#             "book_reading_progress": float(book_data.get("book_reading_progress", 0.0)),
#             "book_quiz_participated": 0,
#             "book_quiz_won": 0,
#             "book_quiz_prizes_won": 0,
#             "book_quiz_score": 0.0,
#             "added_at": datetime.utcnow(),
#         }

#         # Update database
#         await users_collection.update_one(
#             {"_id": ObjectId(user_id)},
#             {
#                 "$push": {"my_library": book_dict},
#                 "$set": {"updated_at": datetime.utcnow()},
#             },
#         )

#         return {"message": "Book added to library successfully"}

#     except Exception as e:
#         print(f"Error adding book to library: {str(e)}")
#         raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/users/library")
async def add_book_to_library(token: str, book_data: dict = None):
    try:
        # Validate token
        payload = verify_access_token(token)
        user_id = payload["user_id"]

        # Get user
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate book_data
        if not book_data:
            raise HTTPException(status_code=400, detail="Book data is required")

        book_id = str(book_data.get("book_id", ""))
        reading_progress = float(book_data.get("book_reading_progress", 0.0))

        # Try to update existing book first
        update_result = await users_collection.update_one(
            {"_id": ObjectId(user_id), "my_library.book_ids": book_id},
            {
                "$set": {
                    "my_library.$.book_name": book_data.get("book_name", ""),
                    "my_library.$.book_author": book_data.get("book_author", ""),
                    "my_library.$.book_cover": book_data.get("book_cover", ""),
                    "my_library.$.book_reading_progress": reading_progress,
                    "updated_at": datetime.utcnow(),
                }
            },
        )

        # If no book was updated (doesn't exist), insert new one
        if update_result.modified_count == 0:
            book_dict = {
                "book_ids": book_id,
                "book_name": book_data.get("book_name", ""),
                "book_author": book_data.get("book_author", ""),
                "book_cover": book_data.get("book_cover", ""),
                "book_reading_progress": reading_progress,
                "book_quiz_participated": 0,
                "book_quiz_won": 0,
                "book_quiz_prizes_won": 0,
                "book_quiz_score": 0.0,
                "added_at": datetime.utcnow(),
            }

            await users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$push": {"my_library": book_dict},
                    "$set": {"updated_at": datetime.utcnow()},
                },
            )
            return {"message": "Book added to library successfully"}
        else:
            return {"message": "Book updated in library successfully"}

    except Exception as e:
        print(f"Error adding book to library: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/users/purchase-history")
async def add_purchase_history(token: str, history: dict = None):
    try:
        # Validate token
        payload = verify_access_token(token)
        user_id = payload["user_id"]

        # Get user
        user = await UserService.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate book_data
        if not history:
            raise HTTPException(status_code=400, detail="Book data is required")

        book_id = str(history.get("book_id", ""))

        # If no book was updated (doesn't exist), insert new one

        history_dict = {
            "book_id": book_id,
            "purchase_date": datetime.utcnow(),
            "amount_paid": history.get("amount_paid", ""),
            "transaction_id": history.get("transaction_id", ""),
        }

        book_dict = {
            "book_ids": book_id,
            "book_name": history.get("book_name", ""),
            "book_author": history.get("book_author", ""),
            "book_cover": history.get("book_cover", ""),
            "book_reading_progress": history.get("book_reading_progress", ""),
            "book_quiz_participated": 0,
            "book_quiz_won": 0,
            "book_quiz_prizes_won": 0,
            "book_quiz_score": 0.0,
            "added_at": datetime.utcnow(),
        }

        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$push": {"purchase_history": history_dict, "my_library": book_dict},
                "$set": {"updated_at": datetime.utcnow()},
            },
        )
        return {"message": "purchase history added successfully"}

    except Exception as e:
        print(f"Error adding purchase history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# get user library books details
@router.get("/user-library")
async def get_user_library_books(userId: str = None):    
    try:
        # Validate input

        if not userId or not userId.strip():
            raise HTTPException(status_code=400, detail="userId parameter is required")
        
        if not ObjectId.is_valid(userId):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        # Get user document
        user = await users_collection.find_one({"_id": ObjectId(userId)})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Handle case where my_library doesn't exist
        if "my_library" not in user:
            return {
                "user_id": userId,
                "book_data": [],
                "message": "Library is empty"
            }
        
        my_library = user.get("my_library", [])
        
        # If my_library is empty list
        if not my_library:
            return {
                "user_id": userId,
                "book_data": [],
                "message": "Library is empty"
            }
        
        # Extract book_ids from the list of objects
   
        book_ids = []
        for item in my_library:
            if isinstance(item, dict) and "book_ids" in item:
                # Convert string book_id to ObjectId
                try:
                    if ObjectId.is_valid(item["book_ids"]):
                        book_ids.append(ObjectId(item["book_ids"]))
                except:
                    # Skip invalid book_ids
                    continue
        
        # If no valid book_ids found
        if not book_ids:
            return {
                "user_id": userId,
                "book_data": [],
                "message": "No valid book IDs found in library"
            }
        
        # Get complete book details from books collection
        books_from_db = await books_collection.find(
            {"_id": {"$in": book_ids}}
        ).to_list(length=None)
        
        # Create a mapping of book_id to book document for quick lookup
        book_map = {}
        for book in books_from_db:
            book_id_str = str(book["_id"])
            # Clean up the book document for response
            book["_id"] = book_id_str
            book_map[book_id_str] = book
        
        # Enrich my_library items with complete book data
        enriched_library = []
        for library_item in my_library:
            if isinstance(library_item, dict) and "book_ids" in library_item:
                book_id = library_item["book_ids"]
                
                # Create enriched item
                enriched_item = {
                    "library_info": {
                        "added_at": library_item.get("added_at"),
                        "reading_progress": library_item.get("book_reading_progress", 0),
                        "quiz_participated": library_item.get("book_quiz_participated", 0),
                        "quiz_won": library_item.get("book_quiz_won", 0),
                        "quiz_score": library_item.get("book_quiz_score", 0),
                        "prizes_won": library_item.get("book_quiz_prizes_won", 0)
                    }
                }
                
                # Add book details if available in books collection
                if book_id in book_map:
                    enriched_item.update(book_map[book_id])
                else:
                    # Use the basic info from my_library as fallback
                    enriched_item.update({
                        "_id": book_id,
                        "title": library_item.get("book_name", "Unknown Title"),
                        "author": library_item.get("book_author", "Unknown Author"),
                        "cover_image": library_item.get("book_cover"),
                        "is_from_library_only": True  # Flag to indicate data is from library, not books collection
                    })
                
                enriched_library.append(enriched_item)
        
        return {
            "user_id": userId,
            "total_books": len(enriched_library),
            "book_data": enriched_library
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching library: {str(e)}")


# ========== REMOVE BOOK FROM LIBRARY ==========
@router.delete("/user-library/remove-book")
async def remove_book_from_library(  userId: str = Query(..., description="User ID"), bookId: str = Query(..., description="Book ID")):
    """
    Remove a book from user's library
    """
    try:
        if not ObjectId.is_valid(userId):
            raise HTTPException(status_code=400, detail="Invalid user ID format")
        
        user = await users_collection.find_one({"_id": ObjectId(userId)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        my_library = user.get("my_library", [])
        
        # Filter out the book to remove
        updated_library = [
            item for item in my_library 
            if not (isinstance(item, dict) and item.get("book_ids") == bookId)
        ]
        
        # Update the database
        update_result = await users_collection.update_one(
            {"_id": ObjectId(userId)},
            {
                "$set": {
                    "my_library": updated_library,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        removed_count = len(my_library) - len(updated_library)
        
        return {
            "success": True,
            "message": f"Removed {removed_count} book(s) from library",
            "books_remaining": len(updated_library)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#  sign-up with email
@router.post("/users/register")
async def sign_up_user(user_data: dict):
    # return await UserService.create_user(user_data)
    print("Signing up user with data:", user_data)
    print("User data received:", user_data.get("name"), user_data.get("email"))
    # Check if user already exists with same email
    existing_user = await users_collection.find_one({"email": user_data.get("email")})

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create new user
    new_user = {
        "email": user_data.get("email"),
        "display_name": user_data.get("name", ""),
        "profile_picture": user_data.get("profile_picture", ""),
        "is_active": True,
        "membership_tier": "free",
        "social_auth": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
    }
    try:
        new_user["password"] = hash_password(
            user_data.get("password")
        )  # In real app, hash the password
        result = await users_collection.insert_one(new_user)
        new_user["_id"] = str(result.inserted_id)
        created_user = UserInDB(**new_user)

        # ✅ Create JWT Token
        jwt_token = create_access_token(
            {
                "email": user_data.get("email"),
                "user_id": str(result.inserted_id),
                "provider": "email",
            }
        )

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user_id": str(result.inserted_id),
            "email": user_data.get("email"),
            "name": user_data.get("name", ""),
            "profile_picture": user_data.get("profile_picture", ""),
        }
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")


@router.post("/users/login")
async def login_user(user_data: dict):
    existing_user = await users_collection.find_one({"email": user_data.get("email")})
    print("Existing user:", existing_user)
    if not existing_user:
        raise HTTPException(status_code=404, detail="Invalid credentials")

    if not verify_password(user_data.get("password"), existing_user.get("password")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last login time
    existing_user["last_login"] = datetime.utcnow()
    await UserService.update_user(existing_user.get("_id"), UserUpdate())

    # ✅ Create JWT Token
    jwt_token = create_access_token(
        {
            "email": existing_user.get("email"),
            "user_id": str(existing_user.get("_id")),
            "provider": "email",
        }
    )

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user_id": str(existing_user.get("_id")),
        "email": existing_user.get("email"),
        "name": existing_user.get("display_name", ""),
        "profile_picture": existing_user.get("profile_picture", ""),
    }
