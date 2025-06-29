from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Debug: Check if Langfuse environment variables are loaded
print("=== ENVIRONMENT VARIABLES DEBUG ===")
print(f"LANGFUSE_PUBLIC_KEY: {os.getenv('LANGFUSE_PUBLIC_KEY', 'NOT SET')}")
print(f"LANGFUSE_SECRET_KEY: {os.getenv('LANGFUSE_SECRET_KEY', 'NOT SET')[:10]}..." if os.getenv('LANGFUSE_SECRET_KEY') else "LANGFUSE_SECRET_KEY: NOT SET")
print(f"LANGFUSE_HOST: {os.getenv('LANGFUSE_HOST', 'NOT SET')}")
print(f"ANTHROPIC_API_KEY: {os.getenv('ANTHROPIC_API_KEY', 'NOT SET')[:10]}..." if os.getenv('ANTHROPIC_API_KEY') else "ANTHROPIC_API_KEY: NOT SET")
print("==================================")

from app.api.routes import router
from app.core.config import settings
from app.core.tracing import tracing_service
from app.api.middleware import setup_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events"""
    
    # Startup
    logger.info("Starting LetterChain API...")
    logger.info(f"Environment: {'DEBUG' if settings.DEBUG else 'PRODUCTION'}")
    logger.info(f"Tracing enabled: {settings.ENABLE_TRACING}")
    
    # Initialize services
    try:
        # Test Redis connection
        from app.services.cache_service import cache_service
        cache_service._test_connection()
        logger.info("Cache service initialized")
        
        # Test AI service
        from app.services.ai_service import ai_service
        logger.info("AI service initialized")
        
        # Test tracing
        if settings.ENABLE_TRACING:
            logger.info("Tracing service initialized")
        
    except Exception as e:
        logger.error(f"Service initialization failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down LetterChain API...")
    
    # Cleanup resources
    try:
        # Close Redis connection
        from app.services.cache_service import cache_service
        cache_service.redis_client.close()
        logger.info("Cache service shutdown complete")
        
    except Exception as e:
        logger.error(f"Shutdown cleanup failed: {str(e)}")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="AI-powered cover letter generation API",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Include API routes
    app.include_router(
        router,
        prefix=settings.API_V1_STR,
        tags=["cover-letters"]
    )
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "LetterChain API",
            "version": settings.VERSION,
            "docs": "/docs" if settings.DEBUG else "Documentation disabled in production"
        }
    
    # Health check endpoint
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "environment": "development" if settings.DEBUG else "production"
        }
    
    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )     