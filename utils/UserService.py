
import os
from datetime import datetime
from typing import Optional 
from fastapi import HTTPException
from models.user_models import UserCreate, UserInDB, SocialAuthProvider, UserUpdate, QuizParticipation, ReadingProgress



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
        
        user_dict = user_data.dict()
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        user_dict["last_login"] = datetime.utcnow()
        
        result = await users_collection.insert_one(user_dict)
        user_dict["_id"] = str(result.inserted_id)
        
        return UserInDB(**user_dict)
    
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
        user_data = users_collection.find_one({"_id": user_id})
        if user_data:
            return UserInDB(**user_data)
        return None
    
    @staticmethod
    async def get_user_by_social_auth(provider: SocialAuthProvider, provider_user_id: str) -> Optional[UserInDB]:
        user_data = users_collection.find_one({
            "social_auth.provider": provider,
            "social_auth.provider_user_id": provider_user_id
        })
        if user_data:
            return UserInDB(**user_data)
        return None
    
    @staticmethod
    async def update_user(user_id: str, update_data: UserUpdate) -> UserInDB:
        update_dict = update_data.dict(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()
        
        users_collection.update_one(
            {"_id": user_id},
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
        
        users_collection.update_one(
            {"_id": user_id},
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
