from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="Supervisor Workers Agent",
    description="FastAPI application with Jinja2 templating",
    version="0.1.0"
)

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Home",
            "message": "Welcome to FastAPI with Jinja2!"
        }
    )


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """Render the about page"""
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "title": "About",
            "description": "This is a FastAPI application with Jinja2 templating support."
        }
    )


@app.get("/api/health")
async def health_check():
    """API endpoint for health check"""
    return {"status": "healthy", "message": "API is running"}


@app.get("/api/data")
async def get_data():
    """Sample API endpoint returning JSON data"""
    return {
        "items": [
            {"id": 1, "name": "Item 1", "description": "First item"},
            {"id": 2, "name": "Item 2", "description": "Second item"},
            {"id": 3, "name": "Item 3", "description": "Third item"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
