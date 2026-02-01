"""FastAPI application factory and setup.

Initializes the FastAPI application with middleware, exception handlers,
and route registration.
"""

# Load environment variables from .env file FIRST
from dotenv import load_dotenv
import os
load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

from app.config import settings
from app.utils.logger import setup_logging
from app.utils.exceptions import AppException
from app.utils.response import create_error_response
from app.database.session import check_db_connection, init_db
from agents import set_tracing_disabled
from app.agents.openrouter_client import setup_openrouter_client
from app.middleware.request_logger import setup_request_logging

# Setup OpenAI Agents SDK to use OpenRouter's OpenAI-compatible endpoint
# This uses OpenRouter's native OpenAI compatibility with Qwen models
setup_openrouter_client()

# Disable tracing since we're using OpenRouter (not OpenAI)
# This prevents the SDK from trying to export traces to OpenAI backend
set_tracing_disabled(disabled=True)

# Setup logging
logger = setup_logging(__name__)

# Create FastAPI appr
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    debug=settings.debug,
)

# Request Logging Middleware - Must be added FIRST (before other middleware)
# This ensures all requests are logged regardless of other middleware
setup_request_logging(app)

# CORS Middleware - Must be added AFTER request logging middleware
# This ensures CORS headers are set for all requests
#
# IMPORTANT FOR REACT NATIVE MOBILE APPS:
# Mobile apps (React Native, Flutter) don't send Origin headers like web browsers.
# We must use allow_origins=["*"] to support mobile apps.
# When allow_origins=["*"], allow_credentials MUST be False (CORS spec requirement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # Should be ["*"] for mobile app support
    allow_credentials=settings.allow_credentials,  # Must be False when origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Log CORS configuration
logger.info(f"CORS enabled for origins: {settings.allowed_origins}")
logger.info(f"CORS allow credentials: {settings.allow_credentials}")


# OPTIONS Handler for CORS Preflight
@app.options("/{full_path:path}")
async def preflight_handler(full_path: str):
    """Handle CORS preflight requests for mobile apps.

    Mobile apps (React Native, Flutter, etc.) send OPTIONS requests before
    actual requests to check CORS permissions. This handler ensures all
    preflight requests are properly handled with appropriate headers.
    """
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "message": "CORS preflight successful"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "3600",
        },
    )


# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    logger.error(f"AppException: {exc.code} - {exc.message}")
    return create_error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc.errors()}")
    return create_error_response( 
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=status.HTTP_400_BAD_REQUEST,
        details=exc.errors(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(f"Unexpected error: {exc}")
    return create_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Check application and database health.

    This endpoint is designed for mobile app health checks and monitoring.
    Mobile apps can use this to verify backend connectivity before making
    authenticated requests.

    Returns:
        dict: Health status with detailed information
    """
    from fastapi.responses import JSONResponse
    import time

    db_ok = check_db_connection()
    is_healthy = db_ok

    response_data = {
        "status": "healthy" if is_healthy else "degraded",
        "timestamp": int(time.time()),
        "services": {
            "database": "ok" if db_ok else "error",
            "api": "ok",
        },
        "version": settings.app_version,
        "environment": settings.environment,
    }

    return JSONResponse(
        status_code=200 if is_healthy else 503,
        content=response_data,
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        },
    )


# API Route Registration
from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.agent import router as agent_router
from app.api.events import router as events_router
from app.api.notifications import router as notifications_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["Tasks"])
app.include_router(agent_router, prefix="/api/v1/agent", tags=["Agent"])
app.include_router(events_router, prefix="/api/v1", tags=["Events"])
app.include_router(notifications_router, prefix="/api/v1", tags=["Notifications"])

# API Documentation
@app.get("/docs", tags=["Documentation"], include_in_schema=False)
async def swagger_docs():
    """Swagger UI documentation."""
    return app.openapi()


@app.get("/redoc", tags=["Documentation"], include_in_schema=False)
async def redoc_docs():
    """ReDoc documentation."""
    return app.openapi()


# Startup Events
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.app_name} (v{settings.app_version})")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Check database connection
    if check_db_connection():
        logger.info("Database connection OK")
        # Initialize database schema if it doesn't exist
        try:
            init_db()
            logger.info("Database schema initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize database schema: {e}")
            logger.info("Continuing startup - tables may already exist")
    else:
        # In development, warn but don't crash if database unavailable
        if settings.is_development:
            logger.warning("Database connection failed - app running in degraded mode")
            logger.warning("To use database features, set DATABASE_URL to a valid Neon connection")
            logger.warning("Get started at: https://console.neon.tech")
        else:
            # In production, database is required
            logger.error("Failed to connect to database")
            raise RuntimeError("Database connection required in production environment")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.app_name}")


# Import cache utility
from app.utils.cache import invalidate_cache

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint.

    Returns:
        dict: API information
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


# Event handlers for cache invalidation
@app.middleware("http")
async def cache_invalidation_middleware(request, call_next):
    """Invalidate cache when tasks are modified."""
    response = await call_next(request)

    # Invalidate task cache after successful write operations
    if request.method in ["POST", "PUT", "PATCH", "DELETE"] and "/tasks" in str(request.url):
        if 200 <= response.status_code < 300:
            # Invalidate all task-related cache entries
            from app.utils.logger import setup_logging
            logger = setup_logging(__name__)
            logger.info(f"Invalidating cache after {request.method} request to {request.url}")
            invalidate_cache("get_user_tasks:")
            invalidate_cache("get_task:")

    return response
