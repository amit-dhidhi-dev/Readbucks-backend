from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
import httpx
from models.user_models import UserCreate, SocialAuthInfo
from database.connection import database as db
from utils.token import create_access_token


router = APIRouter(prefix="/auth", tags=["Google Auth"])


@router.post("/google")
async def google_auth(data: dict):
    """
    Google OAuth login/signup route
    Frontend se: { "access_token": "<google_access_token>" } aayega
    """
    try:
        access_token = data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token is required")

        # ✅ Step 1: Verify token & fetch user info from Google API
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Invalid or expired Google token"
            )

        google_data = response.json()
        google_id = google_data.get("id")
        email = google_data.get("email")

        if not google_id or not email:
            raise HTTPException(status_code=400, detail="Invalid Google user data")

        # ✅ Step 2: Check if user already exists
        user = await db.users.find_one(
            {
                "social_auth.provider": "google",
                "social_auth.provider_user_id": google_id,
            }
        )

        # ✅ Step 3: Create new user if not exists
        if not user:
            # new_user = UserCreate(
            #     email=email,
            #     display_name=google_data.get("name", ""),
            #     profile_picture=google_data.get("picture"),
            #     is_active=True,
            #     membership_tier="free",
            #     social_auth=[SocialAuthInfo(
            #         provider="google",
            #         provider_user_id=google_id,
            #         email=email,
            #         access_token=access_token,
            #         refresh_token=None,
            #         expires_at=None,
            #     )],
            # )
            
            new_user = {
                "email": email,
                "display_name": google_data.get("name", ""),
                "profile_picture": google_data.get("picture"),
                "is_active": True,
                "membership_tier": "free",
                "social_auth": [
                    {
                        "provider": "google",
                        "provider_user_id": google_id,
                        "email": email,
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
            # result = await db.users.insert_one(new_user.dict(by_alias=True))
            # print("user created")
            user_id = str(result.inserted_id)
        else:
            # print("user exists")
            user_id = str(user["_id"])
            # Update last login timestamp
            await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}}
             )

        # ✅ Step 4: Create and return JWT token
        jwt_token = create_access_token(
            {"user_id": user_id, "email": email, "provider": "google"}
        )     

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user_id": user_id,
            "email": email,
            "name": google_data.get("name", ""),
            "profile_picture": google_data.get("picture"),
        }

    except httpx.RequestError:
        raise HTTPException(
            status_code=500, detail="Unable to connect to Google servers"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
