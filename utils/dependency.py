from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from utils.UserService import UserService
from utils.token import verify_access_token  # adjust path to your token utilities
from typing import  Optional
from datetime import datetime
import uuid

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    payload = verify_access_token(token.credentials)
    user = await UserService.get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def get_content_type(filename: str, file_type: str = "image"):
    """Determine content type based on file extension and type"""
    file_extension = filename.lower().split('.')[-1]
    
    mime_types = {
        "image": {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'svg': 'image/svg+xml',
            'bmp': 'image/bmp',
            'ico': 'image/x-icon'
        },
        "document": {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'epub': 'application/epub+zip'
        }
    }
    
    content_type_map = mime_types.get(file_type, {})
    return content_type_map.get(file_extension, 'application/octet-stream')


def generate_unique_filename(original_filename: str, custom_name: Optional[str] = None) -> str:
    """
    Generate a unique filename to prevent collisions
    Format: [custom_name_or_uuid]_[timestamp]_[random_string].[extension]
    """
    # Extract file extension
    file_extension = original_filename.lower().split('.')[-1]
    
    # Generate unique components
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_str = uuid.uuid4().hex[:8]  # First 8 chars of UUID
    
    # Use custom name if provided, otherwise use original name without extension
    if custom_name:
        name_base = custom_name.replace(' ', '_').lower()
    else:
        name_base = original_filename.rsplit('.', 1)[0].replace(' ', '_').lower()
    
    # Create unique filename
    unique_filename = f"{name_base}_{timestamp}_{random_str}.{file_extension}"
    
    return unique_filename