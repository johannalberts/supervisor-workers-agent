"""
HTML Pages Router
Handles all HTML page rendering endpoints
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings

router = APIRouter(tags=["pages"])

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    """
    Render the home page with chat interface
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Home",
            "message": "Welcome to FastAPI with Jinja2!"
        }
    )


@router.get("/about", response_class=HTMLResponse, name="about")
async def about(request: Request):
    """
    Render the about page
    """
    return templates.TemplateResponse(
        "about.html",
        {
            "request": request,
            "title": "About",
            "description": "This is a FastAPI application with Jinja2 templating support and a supervisor-workers agent architecture."
        }
    )
