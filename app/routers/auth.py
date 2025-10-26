"""
Authentication Router
Handles user registration, login, and authentication
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.database import get_database
from app.core.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_active_user
)
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])
templates = Jinja2Templates(directory=str(settings.templates_dir))


@router.get("/signup", response_class=HTMLResponse, name="signup_page")
async def signup_page(request: Request):
    """
    Render the sign up page
    """
    return templates.TemplateResponse(
        "signup.html",
        {"request": request, "title": "Sign Up"}
    )


@router.get("/login", response_class=HTMLResponse, name="login_page")
async def login_page(request: Request):
    """
    Render the login page
    """
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": "Log In"}
    )


@router.post("/signup")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    db = Depends(get_database)
):
    """
    Register a new user
    
    Args:
        request: FastAPI request object
        email: User email
        password: User password
        first_name: User first name
        last_name: User last name
        db: Database connection
        
    Returns:
        Redirect to home page with token set as cookie
        
    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        return templates.TemplateResponse(
            "signup.html",
            {
                "request": request,
                "error": "Email already registered"
            }
        )
    
    # Create user document
    user_doc = {
        "email": email,
        "hashed_password": get_password_hash(password),
        "first_name": first_name,
        "last_name": last_name,
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Insert user into database
    result = await db.users.insert_one(user_doc)
    user_doc["id"] = str(result.inserted_id)
    
    # Create indexes on email field
    await db.users.create_index("email", unique=True)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user_doc["email"]}, expires_delta=access_token_expires
    )
    
    # Redirect to home page and set cookie
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite="lax"
    )
    
    return response


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db = Depends(get_database)
):
    """
    Login user and return JWT token
    
    Args:
        request: FastAPI request object
        email: User email
        password: User password
        db: Database connection
        
    Returns:
        Redirect to home page with token set as cookie
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    user = await db.users.find_one({"email": email})
    
    # Verify user exists and password is correct
    if not user or not verify_password(password, user["hashed_password"]):
        # Return to login page with error
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Incorrect email or password"
            }
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Redirect to home page and set cookie
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=settings.access_token_expire_minutes * 60,
        samesite="lax"
    )
    
    return response


@router.get("/logout")
async def logout():
    """
    Logout user by clearing the authentication cookie
    
    Returns:
        Redirect to login page with cookie cleared
    """
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    """
    Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data
    """
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        first_name=current_user["first_name"],
        last_name=current_user["last_name"],
        created_at=current_user["created_at"],
        is_active=current_user.get("is_active", True)
    )
