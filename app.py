"""
Render-optimized entry point for RAG API
"""
import os
import sys
import logging
from main import app

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    
    # Render sets PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    logger.info(f"🚀 Starting RAG API on port {port}")
    logger.info(f"🌍 Environment: {os.environ.get('APP_ENV', 'development')}")
    
    # Render-optimized uvicorn config
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        loop="asyncio",  # Use standard asyncio for Render compatibility
        workers=1  # Single worker for free tier
    )