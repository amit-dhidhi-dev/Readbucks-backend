from fastapi import FastAPI
from database.connection import check_connection
from routes.user_routes import router as user_router
from routes.auth.google import router as google_auth_router
from routes.auth.facebook import router as facebook_auth_router
from routes.book_routes import router as book_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from utils.pdf_service import process_book 
import asyncio  # Add this import
import os
import routes.payment_routes as payment_routes
import services.search as search_routes

# FastAPI app create karein
app = FastAPI(
    title="FastAPI MongoDB Backend",
    description="Complete backend with FastAPI and MongoDB",
    version="1.0.0"
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# // create folder for temp file 
os.makedirs(os.environ["TEMP_DIR"], exist_ok=True)
# os.makedirs(os.environ["TEMP_COVER"], exist_ok=True)


# routes for google login
app.include_router(google_auth_router)
# routes for facebook login
app.include_router(facebook_auth_router)

# Routes include karein
app.include_router(user_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")

# Include payment routes
app.include_router(payment_routes.router)



# include search routes
app.include_router(search_routes.router, prefix="/api/v1")




# Startup event
@app.on_event("startup")
async def startup_event():
    await check_connection();
 
# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI MongoDB Backend!",
        "status": "running",
        "docs": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}




from utils.book_convertor import BookConvertor
from models.book_models import BookInDB
data =  {
  "title": "startups",
  "subtitle": "",
  "author": "amit dhdihi",
  "co_authors": [],
  "publisher": "readbucks",
  "isbn": '',
  "description": "this is short description about startups",
  "long_description": "",
  "categories": [
    "educational"
  ],
  "language": "english",
  "tags": [],
  "access_level": "paid",
  "status": "published",
  "cover_image_url": "https://4e2de902c9c96022ca5a34538b962d83.r2.cloudflarestorage.com/ebookstorage/images/cover_20251109_144419_0d057838.png",
  "book_content_url": {
    "docx": None,
    "pdf": None,
    "epub": "https://4e2de902c9c96022ca5a34538b962d83.r2.cloudflarestorage.com/ebookstorage/documents/calibre_20251109_144423_249310e7.epub"
  },
  "sample_chapter_url": None,
  "price": 0.0,
  "discount_price": 0.0,
  "is_free": True,
  "total_pages": 233,
  "word_count": 0,
  "publication_date": "2025-11-03 00:00:00+00:00",
  "edition": "1st",
  "estimated_reading_time": 0,
  "difficulty_level": "beginner",
  "id": "69105b83daa2369b47fba507",
  "chapters": [],
  "quizzes": [],
  "reviews": [],
  "total_ratings": 0,
  "average_rating": 0.0,
  "total_reviews": 0,
  "total_purchases": 0,
  "total_reads": 0,
  "total_quiz_attempts": 0,
  "created_by": "690787a7a6273a592459f2e1",
  "created_at": "2025-11-09 09:14:43.327000",
  "updated_at": "2025-11-09 09:14:43.327000",
  "published_at": "2025-11-09 09:14:43.327000"
}
# BookConvertor(BookInDB(**data) )

if __name__ == "__main__":
    # asyncio.run(heelo());
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )