from fastapi import APIRouter, HTTPException, status
from database.connection import database
# from models.user_models import User, UserInDB, UpdateUser
from bson import ObjectId
from typing import List

router = APIRouter()
# collection = database["users"]

# # Helper function - ObjectId ko string mein convert kare
# def user_helper(user) -> dict:
#     return {
#         "id": str(user["_id"]),
#         "name": user["name"],
#         "email": user["email"],
#         "age": user["age"],
#         "city": user.get("city", ""),
#         # "created_at": user.get("created_at","")
#     }

# # Create New User
# @router.post("/users/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
# async def create_user(user: User):
#     # Check if email already exists
#     existing_user = await collection.find_one({"email": user.email})
#     if existing_user:
#         raise HTTPException(
#             status_code=400,
#             detail="Email already registered"
#         )
    
#     user_dict = user.dict()
#     result = await collection.insert_one(user_dict)
    
#     # Inserted document ko retrieve karein
    
#     try:    
#         new_user = await collection.find_one({"_id": result.inserted_id})
#         print(f"New user created with ID: {result.inserted_id, new_user, result}")
#         # print(f"create at {new_user['created_at']}")
#         return user_helper(new_user)
#     except Exception as e:
#         print(f"Error retrieving new user: {e}")
#         return {"error": "Failed to retrieve new user"} 
#     # return UserInDB(
#     #     id=str(result.inserted_id),
#     #     **user.dict()
#     # )

# # Get All Users
# @router.get("/users/", response_model=List[UserInDB])
# async def get_all_users(skip: int = 0, limit: int = 10):
#     users = []
#     async for user in collection.find().skip(skip).limit(limit):
#         users.append(user_helper(user))
#     return users

# # Get Single User by ID
# @router.get("/users/{user_id}", response_model=UserInDB)
# async def get_user(user_id: str):
#     if not ObjectId.is_valid(user_id):
#         raise HTTPException(status_code=400, detail="Invalid user ID")
    
#     user = await collection.find_one({"_id": ObjectId(user_id)})
#     if user:
#         return user_helper(user)
#     raise HTTPException(status_code=404, detail="User not found")

# # Update User
# @router.put("/users/{user_id}", response_model=UserInDB)
# async def update_user(user_id: str, user_data: UpdateUser):
#     if not ObjectId.is_valid(user_id):
#         raise HTTPException(status_code=400, detail="Invalid user ID")
    
#     # Remove None values from update data
#     update_data = {k: v for k, v in user_data.dict().items() if v is not None}
    
#     if not update_data:
#         raise HTTPException(status_code=400, detail="No data provided for update")
    
#     result = await collection.update_one(
#         {"_id": ObjectId(user_id)},
#         {"$set": update_data}
#     )
    
#     if result.modified_count == 1:
#         updated_user = await collection.find_one({"_id": ObjectId(user_id)})
#         return user_helper(updated_user)
    
#     raise HTTPException(status_code=404, detail="User not found")

# # Delete User
# @router.delete("/users/{user_id}")
# async def delete_user(user_id: str):
#     if not ObjectId.is_valid(user_id):
#         raise HTTPException(status_code=400, detail="Invalid user ID")
#
#     result = await collection.delete_one({"_id": ObjectId(user_id)})
#     if result.deleted_count == 1:
#         return {"message": "User deleted successfully"}
#
#     raise HTTPException(status_code=404, detail="User not found")



from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
from pymongo import MongoClient
from pymongo.collection import Collection
import os
from typing import List
from models.user_models import UserCreate, UserInDB, UserResponse, UserStatsResponse, SocialAuthProvider, UserUpdate, QuizParticipation, ReadingProgress
from database.connection import database
from datetime import datetime
from typing import Optional
from bson import ObjectId
from utils.token import verify_access_token, create_access_token, hash_password, verify_password


app = FastAPI()
security = HTTPBearer()

# MongoDB connection
# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
# client = MongoClient(MONGODB_URL)
# db = client["ebook_platform"]
# users_collection: Collection = db["users"]
users_collection  = database["users"]

class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> UserInDB:
        # Check if user already exists with same social auth
        existing_user = await users_collection.find_one({
            "social_auth.provider": user_data.social_auth.provider,
            "social_auth.provider_user_id": user_data.social_auth.provider_user_id
        })
        
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
    async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
        user_data = await users_collection.find_one({"_id": ObjectId(user_id)})
      
        if user_data and isinstance(user_data.get("_id"), ObjectId):
           user_data["_id"] = str(user_data["_id"])
        if user_data:
            return UserInDB(**user_data)
        return None
    
    @staticmethod
    async def get_user_by_social_auth(provider: SocialAuthProvider, provider_user_id: str) -> Optional[UserInDB]:
        user_data = await users_collection.find_one({
            "social_auth.provider": provider,
            "social_auth.provider_user_id": provider_user_id
        })
        if user_data:
            return UserInDB(**user_data)
        return None
    
    @staticmethod
    async def update_user(user_id: str, update_data: UserUpdate) -> UserInDB:
        update_dict =  update_data.dict(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()

        
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_dict}
        )

        return await UserService.get_user_by_id(user_id)
    
    @staticmethod
    async def add_quiz_participation(user_id: str, quiz_data: QuizParticipation) -> UserInDB:
        quiz_dict = quiz_data.dict()
        
        update_data = {
            "$push": {"quiz_participations": quiz_dict},
            "$set": {"updated_at": datetime.utcnow()}
        }
        
        if quiz_data.is_winner:
            update_data["$inc"] = {
                "total_quiz_wins": 1,
                "total_prize_money": quiz_data.prize_amount
            }
        
        await users_collection.update_one(
            {"_id": ObjectId(user_id)},
            update_data
        )
        
        return await UserService.get_user_by_id(user_id)
    
    @staticmethod
    async def update_reading_progress(user_id: str, progress_data: ReadingProgress) -> UserInDB:
        # Remove existing progress for this book
        users_collection.update_one(
            {"_id": user_id},
            {"$pull": {"reading_progress": {"book_id": progress_data.book_id}}}
        )
        
        # Add new progress
        progress_dict = progress_data.dict()
        users_collection.update_one(
            {"_id": user_id},
            {
                "$push": {"reading_progress": progress_dict},
                "$set": {"updated_at": datetime.utcnow()}
            }
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

@router.get("/getCurrentUser", response_model=UserResponse)
async def get_current_user(token: str):
    payload = verify_access_token(token)
    print('payload',payload['user_id'])
    user = await UserService.get_user_by_id(payload['user_id'])
    print("Fetched user:", user)
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
    avg_score = sum([q.score for q in user.quiz_participations]) / total_quizzes if total_quizzes > 0 else 0
    
    return UserStatsResponse(
        user_id=user_id,
        total_quizzes_taken=total_quizzes,
        average_quiz_score=avg_score,
        favorite_genres=[],  # You can implement genre tracking
        reading_streak=0,    # Implement streak logic
        monthly_reading_goal=user.reading_goals.get("monthly", 0),
        monthly_reading_progress=user.reading_goals.get("monthly_progress", 0)
    )

#  sign-up with email
@router.post("/users/register")
async def sign_up_user(user_data: dict):  
    # return await UserService.create_user(user_data)
    print("Signing up user with data:", user_data)
    print("User data received:", user_data.get("name"), user_data.get("email"))
     # Check if user already exists with same email
    existing_user = await users_collection.find_one({
        "email": user_data.get("email")
    })
    
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
        "last_login": datetime.utcnow()
    }
    try:
        new_user["password"] = hash_password(user_data.get("password"))  # In real app, hash the password
        result = await users_collection.insert_one(new_user)
        new_user["_id"] = str(result.inserted_id)
        created_user = UserInDB(**new_user)

        # ✅ Create JWT Token
        jwt_token = create_access_token({
            "email":  user_data.get("email"),
            "user_id": str(result.inserted_id),
            "provider": "email"
        })
        
        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user_id": str(result.inserted_id),
            "email":  user_data.get("email"),
            "name": user_data.get("name", ""),
            "profile_picture": user_data.get("profile_picture", ""),
        }
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Error creating user")

@router.post("/users/login")
async def login_user(user_data: dict):
    existing_user = await users_collection.find_one({
        "email": user_data.get("email")
    })
    print("Existing user:", existing_user)
    if not existing_user:
        raise HTTPException(status_code=404, detail="Invalid credentials")

    if not verify_password(user_data.get("password"), existing_user.get("password")):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
    # Update last login time
    existing_user['last_login'] = datetime.utcnow()
    await UserService.update_user(existing_user.get("_id"), UserUpdate())
    
     # ✅ Create JWT Token
    jwt_token = create_access_token({
            "email":  existing_user.get("email"),
            "user_id": str(existing_user.get("_id")),
            "provider": "email"
        })
        
    return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user_id": str(existing_user.get("_id")),
            "email":  existing_user.get("email"),
            "name": existing_user.get("display_name", ""),
            "profile_picture": existing_user.get("profile_picture", ""),
        }