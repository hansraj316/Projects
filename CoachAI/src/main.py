"""Main FastAPI application module for CoachAI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

app = FastAPI(
    title="CoachAI",
    description="A modular AI-learning assistant with multi-agent orchestration",
    version="0.1.0",
    debug=settings.debug
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development() else ["https://your-production-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to CoachAI!",
        "status": "operational",
        "environment": settings.app_env
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.app_env
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development()
    ) 