from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
import httpx
from utils.token import create_access_token
from database.connection import database as db  # MongoDB client

router = APIRouter(prefix="/auth", tags=["facebook Auth"])

@router.post("/facebook")
async def facebook_auth(access_token: str):
    """Facebook OAuth login/signup"""
    try:
        # ✅ Step 1: Verify Facebook Access Token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email,picture",
                    "access_token": access_token
                }
            )

        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid Facebook token")

        fb_data = response.json()

        # ✅ Step 2: Ensure email permission
        if "email" not in fb_data:
            raise HTTPException(status_code=400, detail="Email permission required")

        # ✅ Step 3: Check existing user
        user = await db.users.find_one({
            "social_auth.provider": "facebook",
            "social_auth.provider_user_id": fb_data["id"]
        })

        # ✅ Step 4: If new user, insert
        if not user:
            # print('facebook user created')
            new_user = {
                "email": fb_data["email"],
                "display_name": fb_data.get("name", ""),
                "profile_picture": fb_data.get("picture", {}).get("data", {}).get("url"),
                "is_active": True,
                "membership_tier": "free",
                "social_auth": [
                    {
                        "provider": "facebook",
                        "provider_user_id": fb_data["id"],
                        "email": fb_data["email"],
                        "access_token": access_token,
                        "refresh_token": None,
                        "expires_at": datetime.utcnow()
                    }
                ],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": datetime.utcnow()
            }

            result = await db.users.insert_one(new_user)
            user_id = str(result.inserted_id)

        else:
            # print('facebook user exists')
            # ✅ Step 5: Update last login
            user_id = str(user["_id"])
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"last_login": datetime.utcnow()}}
            )

        # ✅ Step 6: Create JWT Token
        jwt_token = create_access_token({
            "email": fb_data["email"],
            "user_id": user_id,
            "provider": "facebook"
        })

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": fb_data["email"],
            "name": fb_data.get("name", ""),
            "profile_picture": fb_data.get("picture", {}).get("data", {}).get("url"),
        }

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Facebook API error: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Auth error: {str(e)}")









