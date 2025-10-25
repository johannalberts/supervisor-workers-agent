"""
FastAPI Application Main Module
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import api, pages


def create_application() -> FastAPI:
    """
    Application factory pattern
    Creates and configures the FastAPI application
    
    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Mount static files
    app.mount(
        "/static",
        StaticFiles(directory=str(settings.static_dir)),
        name="static"
    )
    
    # Include routers
    app.include_router(pages.router)
    app.include_router(api.router)
    
    return app


# Create app instance
app = create_application()


@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup
    """
    print(f"🚀 {settings.app_name} v{settings.app_version} is starting...")
    print(f"📚 API Documentation: http://{settings.host}:{settings.port}/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on application shutdown
    """
    print(f"👋 {settings.app_name} is shutting down...")
