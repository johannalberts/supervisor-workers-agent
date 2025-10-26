"""
HTML Pages Router
Handles all HTML page rendering endpoints
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.core.config import settings
from app.core.auth import get_current_user_optional

router = APIRouter(tags=["pages"])

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request, current_user: Optional[dict] = Depends(get_current_user_optional)):
    """
    Render the home page with chat interface
    Requires authentication - redirects to login if not authenticated
    """
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Home",
            "message": "Welcome to FastAPI with Jinja2!",
            "user": current_user
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
