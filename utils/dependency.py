from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from utils.UserService import UserService
from utils.token import verify_access_token  # adjust path to your token utilities

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    payload = verify_access_token(token.credentials)
    user = await UserService.get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
