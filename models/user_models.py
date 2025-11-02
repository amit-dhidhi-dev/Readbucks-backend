from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class SocialAuthProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    EMAIL = "email"

class MembershipTier(str, Enum):
    FREE = "free"
    PAID = "paid"
    PREMIUM = "premium"

class ReadingProgress(BaseModel):
    book_id: str
    current_page: int = 0
    total_pages: int
    last_read: datetime = Field(default_factory=datetime.utcnow)
    completion_percentage: float = 0.0

class QuizParticipation(BaseModel):
    quiz_id: str
    book_id: str
    participation_date: datetime = Field(default_factory=datetime.utcnow)
    score: float = 0.0
    max_score: float
    time_taken: int  # in seconds
    rank: Optional[int] = None
    is_winner: bool = False
    prize_amount: float = 0.0
    prize_claimed: bool = False

class PurchaseHistory(BaseModel):
    book_id: str
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    amount_paid: float
    transaction_id: str
    platform: str = "website"

class SocialAuthInfo(BaseModel):
    provider: SocialAuthProvider
    provider_user_id: str
    email: Optional[EmailStr] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    profile_picture: Optional[str] = None
    password: Optional[str] = None
    is_active: bool = True
    membership_tier: MembershipTier = MembershipTier.FREE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)       

class UserCreate(UserBase):
    social_auth: SocialAuthInfo
   
class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    profile_picture: Optional[str] = None
    membership_tier: Optional[MembershipTier] = None
    reading_goals: Optional[Dict[str, Any]] = None

class UserInDB(UserBase):
    id: str = Field(..., alias="_id")
    social_auth:  List[SocialAuthInfo] = []
    reading_progress: List[ReadingProgress] = []
    quiz_participations: List[QuizParticipation] = []
    purchase_history: List[PurchaseHistory] = []
    reading_goals: Dict[str, Any] = {}
    total_quiz_wins: int = 0
    total_prize_money: float = 0.0
    books_purchased: int = 0
    books_completed: int = 0
    total_reading_time: int = 0  # in minutes
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Config:
        # allow_population_by_field_name = True
        validate_by_name=True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Response Models
class UserResponse(UserBase):
    id: str
    total_quiz_wins: int
    total_prize_money: float
    books_purchased: int
    books_completed: int
    total_reading_time: int
    membership_expiry: Optional[datetime] = None
    created_at: datetime

class UserStatsResponse(BaseModel):
    user_id: str
    total_quizzes_taken: int
    average_quiz_score: float
    favorite_genres: List[str]
    reading_streak: int
    monthly_reading_goal: Optional[int] = None
    monthly_reading_progress: int = 0

# Database Indexes (for MongoDB optimization)
USER_INDEXES = [
    {"key": [("email", 1)], "unique": True, "sparse": True},
    {"key": [("social_auth.provider", 1), ("social_auth.provider_user_id", 1)], "unique": True},
    {"key": [("membership_tier", 1)]},
    {"key": [("created_at", -1)]},
    {"key": [("total_quiz_wins", -1)]},
    {"key": [("quiz_participations.quiz_id", 1)]},
    {"key": [("reading_progress.book_id", 1)]}
]