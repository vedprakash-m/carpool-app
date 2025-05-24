import azure.functions as func
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Carpool API", 
    description="API for carpool management with mobile-friendly design. Supports admin, parent, and student roles.",
    version="0.1.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Carpool API is healthy!"}

# Azure Functions entry point
async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions entry point for FastAPI application."""
    from azure.functions._http.asgi import AsgiMiddleware
    asgi_app = AsgiMiddleware(app).handle_async
    return await asgi_app(req)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
