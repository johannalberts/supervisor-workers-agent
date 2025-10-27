"""
Core configuration module
"""
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # App info
    app_name: str = "Supervisor Workers Agent"
    app_version: str = "0.1.0"
    app_description: str = "Customer service chatbot with supervisor-workers architecture"
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # MongoDB settings
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "chatbot"
    
    # JWT settings
    secret_key: str = "your-secret-key-change-this-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI settings
    openai_api_key: str = "your-openai-api-key-here"
    openai_model: str = "gpt-4o-mini"
    
    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    templates_dir: Path = base_dir / "templates"
    static_dir: Path = base_dir / "static"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
