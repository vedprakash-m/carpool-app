from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.db.cosmos import init_cosmos_db
from app.api.v1.api import api_router

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize database and other startup tasks"""
    init_cosmos_db()

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Carpool Management API",
        "version": "1.0.0",
        "docs_url": f"{settings.API_V1_STR}/docs"
    } 