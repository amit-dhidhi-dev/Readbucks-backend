from fastapi import FastAPI
from database.connection import check_connection
from routes.user_routes import router as user_router
from routes.auth.google import router as google_auth_router
from routes.auth.facebook import router as facebook_auth_router
from routes.book_routes import router as book_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


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


# routes for google login
app.include_router(google_auth_router)
# routes for facebook login
app.include_router(facebook_auth_router)

# Routes include karein
app.include_router(user_router, prefix="/api/v1")
app.include_router(book_router, prefix="/api/v1")





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

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )