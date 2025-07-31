"""
Application settings and configuration.
Handles environment variables and Railway deployment settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    app_name: str = "RAG Application API"
    app_env: str = "development"
    debug: bool = False
    
    # Supabase settings
    supabase_url: str
    supabase_service_key: str
    database_url: Optional[str] = None
    
    # Frontend URL for CORS
    frontend_url: str = "http://localhost:3000"
    
    # AI/ML API keys
    together_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # Security settings
    jwt_secret: str = "your-secret-key-change-in-production"
    encryption_key: Optional[str] = None
    secret_key: str = "your-app-secret-change-in-production"
    
    # Rate limiting
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 60
    max_uploads_per_hour: int = 10
    
    # File upload settings
    max_file_size: int = 52428800  # 50MB
    allowed_file_types: str = "pdf,txt,docx,md"
    
    # Railway specific settings
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Railway automatically sets PORT environment variable
        if os.getenv("PORT"):
            self.port = int(os.getenv("PORT"))
            
        # Set production settings if on Railway
        if os.getenv("RAILWAY_ENVIRONMENT"):
            self.app_env = "production"
            self.debug = False
            
        # Use Railway's Redis if available
        if os.getenv("REDIS_URL"):
            self.redis_url = os.getenv("REDIS_URL")

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings