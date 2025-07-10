"""
API router for health check endpoints.
"""

from fastapi import APIRouter
from datetime import datetime
import logging

from api.schemas import HealthResponse


logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Health check for the API service."""
    logger.info("Health check requested.")
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        dependencies={
            "database": "available",
            "orchestrator": "available",
            "external_api": "available"
        }
    )

