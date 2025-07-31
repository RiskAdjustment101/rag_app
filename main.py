"""
Meta-Optimized FastAPI Backend for RAG Application
Production-ready deployment on Railway with Supabase integration
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest

# Import configurations and utilities
from backend.config.settings import get_settings
from backend.auth.middleware import get_current_user
from backend.auth.supabase_client import get_supabase_client

# Configure structured logging (Meta-style)
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp":"%(asctime)s","level":"%(levelname)s","service":"rag-api","message":"%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger("rag-api")

# Production metrics (Meta-style observability)
REQUEST_COUNT = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status', 'version']
)
REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds', 
    'HTTP request latency',
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)
ACTIVE_CONNECTIONS = Counter('active_connections_total', 'Active connections')

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

# Create FastAPI app with Meta-style configuration
app = FastAPI(
    title="RAG Application API",
    description="Meta-optimized backend API for Claude-like RAG application",
    version="1.0.0",
    docs_url="/docs" if get_settings().app_env != "production" else None,
    redoc_url="/redoc" if get_settings().app_env != "production" else None,
    lifespan=lifespan,
    # default_response_class optimized for Railway
    openapi_tags=[
        {"name": "health", "description": "Health check operations"},
        {"name": "auth", "description": "Authentication operations"},
        {"name": "metrics", "description": "Monitoring and metrics"},
    ]
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
async def add_observability_middleware(request: Request, call_next):
    """Meta-style observability middleware with detailed metrics."""
    start_time = time.perf_counter()
    
    # Track active connections
    ACTIVE_CONNECTIONS.inc()
    
    # Get client info for better observability
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    try:
        response = await call_next(request)
        
        # Calculate precise processing time
        process_time = time.perf_counter() - start_time
        
        # Enhanced metrics tracking
        REQUEST_LATENCY.observe(process_time)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            version="v1"
        ).inc()
        
        # Add performance headers
        response.headers.update({
            "X-Process-Time": f"{process_time:.4f}",
            "X-Request-ID": getattr(request.state, "request_id", "unknown"),
            "X-API-Version": "1.0.0"
        })
        
        # Structured logging for requests > 1s (Meta-style alerting)
        if process_time > 1.0:
            logger.warning(
                f"Slow request detected",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration": process_time,
                    "client_ip": client_ip,
                    "status": response.status_code
                }
            )
        
        return response
    
    except Exception as e:
        process_time = time.perf_counter() - start_time
        logger.error(
            f"Request failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration": process_time,
                "error": str(e),
                "client_ip": client_ip
            }
        )
        raise
    finally:
        ACTIVE_CONNECTIONS.dec()

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

@app.get("/health", tags=["health"])
async def health_check():
    """
    Meta-style comprehensive health check with circuit breaker pattern.
    
    Returns:
        Dict containing detailed health status of all services
    """
    start_time = time.perf_counter()
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": settings.app_env,
        "version": "1.0.0",
        "uptime": time.time() - getattr(health_check, "_start_time", time.time()),
        "services": {},
        "metrics": {
            "total_requests": REQUEST_COUNT._value._value,
            "active_connections": ACTIVE_CONNECTIONS._value._value
        }
    }
    
    # Set start time on first call
    if not hasattr(health_check, "_start_time"):
        health_check._start_time = time.time()
    
    # Parallel health checks for better performance
    async def check_supabase():
        try:
            supabase = get_supabase_client()
            if supabase:
                # Quick health check query with timeout
                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        lambda: supabase.table('profiles').select('count').limit(1).execute()
                    ),
                    timeout=2.0
                )
                return {"status": "healthy", "response_time": time.perf_counter() - start_time}
            return {"status": "unavailable", "error": "client_not_initialized"}
        except asyncio.TimeoutError:
            return {"status": "timeout", "error": "health_check_timeout"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def check_redis():
        try:
            if settings.redis_url and "localhost" not in settings.redis_url:
                import redis.asyncio as redis
                r = redis.from_url(settings.redis_url)
                await asyncio.wait_for(r.ping(), timeout=1.0)
                await r.close()
                return {"status": "healthy", "response_time": time.perf_counter() - start_time}
            return {"status": "not_configured"}
        except asyncio.TimeoutError:
            return {"status": "timeout", "error": "redis_timeout"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    # Run health checks concurrently
    supabase_health, redis_health = await asyncio.gather(
        check_supabase(),
        check_redis(),
        return_exceptions=True
    )
    
    health_status["services"]["supabase"] = supabase_health
    health_status["services"]["redis"] = redis_health
    
    # Determine overall status
    unhealthy_services = [
        name for name, service in health_status["services"].items()
        if isinstance(service, dict) and service.get("status") in ["unhealthy", "timeout"]
    ]
    
    if unhealthy_services:
        health_status["status"] = "degraded"
        health_status["unhealthy_services"] = unhealthy_services
    
    # Calculate total health check time
    health_status["health_check_duration"] = time.perf_counter() - start_time
    
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

# API route groups (to be added)
# from api.routes import auth, documents, chat, rag
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
# app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
# app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])

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