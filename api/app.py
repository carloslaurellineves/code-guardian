"""
FastAPI application factory and configuration.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time
from datetime import datetime

from api.routers import test_generation, health, file_upload
from api.middleware.auth import auth_middleware_placeholder
from api.middleware.logging import LoggingMiddleware
from src.config import config


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Code Guardian API...")
    
    # Validate configuration
    try:
        config.validate_required_settings()
        logger.info("Configuration validation successful")
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    # Perform any additional startup checks here
    logger.info("Code Guardian API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Code Guardian API...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="Code Guardian API",
        description="AI-powered unit test generation service",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # Add middleware
    configure_middleware(app)
    
    # Add routers
    configure_routers(app)
    
    # Add exception handlers
    configure_exception_handlers(app)
    
    return app


def configure_middleware(app: FastAPI) -> None:
    """Configure middleware for the application."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for specific domains in production
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
    
    # Custom logging middleware
    app.add_middleware(LoggingMiddleware)
    
    # Add processing time header
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Placeholder for future auth middleware
    # app.add_middleware(auth_middleware_placeholder)


def configure_routers(app: FastAPI) -> None:
    """Configure API routers."""
    
    # Include routers with prefixes
    app.include_router(
        health.router,
        prefix="/health",
        tags=["health"]
    )
    
    app.include_router(
        test_generation.router,
        prefix="/generate",
        tags=["test-generation"]
    )
    
    app.include_router(
        file_upload.router,
        prefix="/upload",
        tags=["file-upload"]
    )


def configure_exception_handlers(app: FastAPI) -> None:
    """Configure custom exception handlers."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation error for {request.url}: {exc}")
        
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": exc.errors(),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception for {request.url}: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# Create the application instance
app = create_app()
