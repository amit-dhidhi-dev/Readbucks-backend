from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum
from bson import ObjectId
from pydantic_core import core_schema

class BookCategory(str, Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    EDUCATIONAL = "educational"
    SELF_HELP = "self_help"
    BUSINESS = "business"
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    HISTORY = "history"
    BIOGRAPHY = "biography"
    OTHER = "other"

class BookLanguage(str, Enum):
    HINDI = "hindi"
    ENGLISH = "english"
    BENGALI = "bengali"
    TAMIL = "tamil"
    TELUGU = "telugu"
    MARATHI = "marathi"
    GUJARATI = "gujarati"
    KANNADA = "kannada"
    MALAYALAM = "malayalam"
    PUNJABI = "punjabi"

class BookStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class BookAccessLevel(str, Enum):
    FREE = "free"
    PAID = "paid"
    PREMIUM = "premium"

class Chapter(BaseModel):
    chapter_number: int
    title: str
    content_url: HttpUrl
    page_count: int
    duration_minutes: int = 0  # Estimated reading time
    is_preview: bool = False  # Free preview chapter

class Quiz(BaseModel):
    quiz_id: str = Field(default_factory=lambda: str(ObjectId()))
    title: str
    description: Optional[str] = None
    questions: List[Dict[str, Any]] = []  # Store quiz questions
    total_questions: int = 0
    time_limit: int = 0  # in minutes, 0 means no limit
    passing_score: float = 60.0  # Percentage
    prize_money: float = 0.0
    max_winners: int = 1
    is_active: bool = True
    start_date: datetime
    end_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Review(BaseModel):
    user_id: str
    user_name: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_verified_purchase: bool = False


class PyObjectId:
    """Pydantic-v2-compatible ObjectId wrapper."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return core_schema.no_info_plain_validator_function(cls.validate)
    
    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise TypeError("Invalid ObjectId")
    
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string", "pattern": "^[0-9a-fA-F]{24}$"}


# two file for book content (pdf/epub)
class BookConentType(BaseModel):
    docx: Optional[HttpUrl] = None
    pdf: Optional[HttpUrl]= None
    epub: Optional[HttpUrl] = None

# Base Book Model
class BookBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    author: str
    co_authors: List[str] = []
    publisher: str
    isbn: Optional[str] = None
    description: str
    long_description: Optional[str] = None
    categories: List[BookCategory] = []
    language: BookLanguage = BookLanguage.HINDI
    tags: List[str] = []
    access_level: BookAccessLevel = BookAccessLevel.PAID
    status: BookStatus = BookStatus.DRAFT

    # Media URLs
    cover_image_url: HttpUrl
    book_content_url: Optional[BookConentType] = None  # Main book content URL (PDF/EPUB/etc)
    sample_chapter_url: Optional[HttpUrl] = None

    # Pricing
    price: float = Field(ge=0)
    discount_price: Optional[float] = Field(None, ge=0)
    is_free: bool = False

    # Book Details
    total_pages: int
    word_count: int = 0
    publication_date: datetime
    edition: str = "1st"

    # Reading metrics
    estimated_reading_time: int = 0  # in minutes
    difficulty_level: str = Field("beginner", pattern="^(beginner|intermediate|advanced)$")

class BookCreate(BookBase):
    chapters: List[Chapter] = []
    quizzes: List[Quiz] = []




class BookUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    discount_price: Optional[float] = None
    status: Optional[BookStatus] = None
    cover_image_url: Optional[HttpUrl] = None
    book_content_url: Optional[BookConentType] = None
    tags: Optional[List[str]] = None

class BookInDB(BookBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    chapters: List[Chapter] = []
    quizzes: List[Quiz] = []
    reviews: List[Review] = []
    
    # Statistics
    total_ratings: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0
    total_purchases: int = 0
    total_reads: int = 0
    total_quiz_attempts: int = 0
    
    # Metadata
    created_by: str  # Admin/Publisher user ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None

    class Config:
        # allow_population_by_field_name = True
        validate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Response Models (without MongoDB specific types)
class BookResponse(BaseModel):
    id: str
    title: str
    subtitle: Optional[str] = None
    author: str
    description: str
    categories: List[BookCategory]
    language: BookLanguage
    cover_image_url: str
    price: float
    discount_price: Optional[float] = None
    is_free: bool
    total_pages: int
    average_rating: float
    total_ratings: int
    total_reviews: int
    access_level: BookAccessLevel
    status: BookStatus
    publication_date: datetime
    estimated_reading_time: int
    has_quizzes: bool = False
    active_quizzes: int = 0

class BookDetailResponse(BookResponse):
    long_description: Optional[str] = None
    chapters: List[Chapter]
    quizzes: List[Quiz]
    reviews: List[Review]
    co_authors: List[str] = []
    publisher: str
    isbn: Optional[str] = None
    tags: List[str] = []
    book_content_url: Optional[BookConentType] = None  # Only for paid users
    sample_chapter_url: Optional[str] = None
    word_count: int
    edition: str
    difficulty_level: str
    total_purchases: int
    total_reads: int

# Search and Filter Models
class BookSearchFilters(BaseModel):
    categories: Optional[List[BookCategory]] = None
    languages: Optional[List[BookLanguage]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_rating: Optional[float] = None
    access_level: Optional[BookAccessLevel] = None
    has_quizzes: Optional[bool] = None
    is_free: Optional[bool] = None

class BookSearchRequest(BaseModel):
    query: Optional[str] = None
    filters: BookSearchFilters = Field(default_factory=BookSearchFilters)
    page: int = 1
    limit: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"