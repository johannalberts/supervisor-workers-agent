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
    
    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    templates_dir: Path = base_dir / "templates"
    static_dir: Path = base_dir / "static"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
