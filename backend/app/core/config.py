from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os

class Settings(BaseSettings):
    """Central configuration using Pydantic for type safety and validation"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LetterChain API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security (REQUIRED in production)
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services (REQUIRED in production)
    ANTHROPIC_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379"
    
    # Langfuse Observability (REQUIRED in production)
    LANGFUSE_PUBLIC_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"
    ENABLE_TRACING: bool = True
    
    # File Upload Limits
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS: set = {".pdf", ".txt", ".docx"}
    ALLOWED_MIME_TYPES: set = {"application/pdf", "text/plain", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 5
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://letterchain05.vercel.app",
        "https://www.letterchain.fyi"
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors_origins(cls, v):
        if isinstance(v, str):
            # Accept comma-separated string from .env
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()