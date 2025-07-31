"""
FastAPI Backend for RAG Application
Hosts on Railway with Supabase integration
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import logging
import time
from typing import Optional

# Import configurations and utilities
from backend.config.settings import get_settings
from backend.auth.middleware import get_current_user
from backend.auth.supabase_client import get_supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import monitoring
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚂 Starting RAG API on Railway...")
    
    # Test Supabase connection
    supabase = get_supabase_client()
    if supabase:
        logger.info("✅ Supabase client initialized")
    else:
        logger.warning("⚠️ Supabase client not available")
    
    yield
    
    logger.info("🛑 Shutting down RAG API...")

# Create FastAPI app
app = FastAPI(
    title="RAG Application API",
    description="Backend API for Claude-like RAG application with document intelligence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        settings.frontend_url,
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_metrics_middleware(request: Request, call_next):
    """Add metrics and timing to all requests."""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Track metrics
    REQUEST_LATENCY.observe(process_time)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    # Add timing header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with logging."""
    logger.error(f"Global exception on {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )

# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "message": "RAG Application API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.app_env,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns:
        Dict containing health status of all services
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.app_env,
        "services": {}
    }
    
    # Check Supabase connection
    try:
        supabase = get_supabase_client()
        if supabase:
            # Simple query to test database
            result = supabase.table('profiles').select('count').limit(1).execute()
            health_status["services"]["supabase"] = "healthy"
        else:
            health_status["services"]["supabase"] = "unavailable"
    except Exception as e:
        logger.error(f"Supabase health check failed: {e}")
        health_status["services"]["supabase"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Check Redis connection (if configured)
    try:
        import redis
        if settings.redis_url and settings.redis_url != "redis://localhost:6379":
            r = redis.from_url(settings.redis_url)
            r.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "not_configured"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = "unhealthy"
        health_status["status"] = "degraded"
    
    # Return appropriate status code
    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")

# Protected endpoint example
@app.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user profile.
    
    Args:
        current_user: Authenticated user from JWT token
        
    Returns:
        User profile information
    """
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "message": "Profile endpoint working!"
    }

# API route groups
from backend.api.documents import router as documents_router
from backend.api.rag import router as rag_router

app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(rag_router, prefix="/api", tags=["RAG"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )