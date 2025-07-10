"""
API router for test generation endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
import time
from datetime import datetime
from typing import Dict, Any

from src.orchestrator import TestGenerationOrchestrator
from api.schemas import (
    TextTestGenerationRequest, 
    GitLabTestGenerationRequest,
    TestGenerationResponse,
    TestGenerationErrorResponse,
    TestGenerationMetadata,
    InputTypeEnum
)
from api.services.orchestrator_service import OrchestratorService

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get orchestrator service
def get_orchestrator_service() -> OrchestratorService:
    """Dependency to provide orchestrator service."""
    return OrchestratorService()


@router.post(
    "/from-text",
    response_model=TestGenerationResponse,
    responses={
        400: {"model": TestGenerationErrorResponse},
        422: {"model": TestGenerationErrorResponse},
        500: {"model": TestGenerationErrorResponse}
    },
    summary="Generate tests from source code text",
    description="Generate unit tests from directly provided source code text"
)
async def generate_from_text(
    request: TextTestGenerationRequest,
    orchestrator_service: OrchestratorService = Depends(get_orchestrator_service)
):
    """Generate unit tests from source code text input."""
    start_time = time.time()
    
    try:
        logger.info(f"Generating tests from text input (language: {request.language})")
        
        # Use the orchestrator service to generate tests
        result = await orchestrator_service.generate_from_text(
            code=request.code,
            language=request.language
        )
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build metadata
        metadata = TestGenerationMetadata(
            input_type=InputTypeEnum.TEXT,
            detected_language=result.get("detected_language"),
            test_framework=result.get("test_framework"),
            processing_time_ms=processing_time,
            lines_of_code=len(request.code.split('\\n'))
        )
        
        if result.get("success"):
            response = TestGenerationResponse(
                success=True,
                generated_tests=result.get("generated_tests", ""),
                metadata=metadata,
                coverage_notes=result.get("coverage_notes"),
                suggestions=result.get("suggestions", []),
                processing_messages=result.get("processing_messages", [])
            )
            logger.info(f"Successfully generated tests from text in {processing_time}ms")
            return response
        else:
            error_response = TestGenerationErrorResponse(
                success=False,
                error=result.get("error", "Unknown error occurred"),
                error_code="GENERATION_FAILED",
                processing_messages=result.get("processing_messages", [])
            )
            logger.error(f"Test generation failed: {result.get('error')}")
            return JSONResponse(status_code=400, content=error_response.dict())
            
    except Exception as e:
        logger.error(f"Unexpected error in generate_from_text: {e}", exc_info=True)
        error_response = TestGenerationErrorResponse(
            success=False,
            error=str(e),
            error_code="INTERNAL_ERROR"
        )
        return JSONResponse(status_code=500, content=error_response.dict())


@router.post(
    "/from-gitlab",
    response_model=TestGenerationResponse,
    responses={
        400: {"model": TestGenerationErrorResponse},
        422: {"model": TestGenerationErrorResponse},
        500: {"model": TestGenerationErrorResponse}
    },
    summary="Generate tests from GitLab repository",
    description="Generate unit tests from a GitLab repository by analyzing its source code"
)
async def generate_from_gitlab(
    request: GitLabTestGenerationRequest,
    orchestrator_service: OrchestratorService = Depends(get_orchestrator_service)
):
    """Generate unit tests from GitLab repository."""
    start_time = time.time()
    
    try:
        logger.info(f"Generating tests from GitLab repository: {request.repo_url}")
        
        # Use the orchestrator service to generate tests
        result = await orchestrator_service.generate_from_gitlab(
            repo_url=request.repo_url,
            access_token=request.access_token,
            branch=request.branch,
            max_files=request.max_files
        )
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Build metadata
        metadata = TestGenerationMetadata(
            input_type=InputTypeEnum.GITLAB,
            detected_language=result.get("detected_language"),
            test_framework=result.get("test_framework"),
            processing_time_ms=processing_time,
            files_processed=result.get("files_processed", 0)
        )
        
        if result.get("success"):
            response = TestGenerationResponse(
                success=True,
                generated_tests=result.get("generated_tests", ""),
                metadata=metadata,
                coverage_notes=result.get("coverage_notes"),
                suggestions=result.get("suggestions", []),
                processing_messages=result.get("processing_messages", [])
            )
            logger.info(f"Successfully generated tests from GitLab repository in {processing_time}ms")
            return response
        else:
            error_response = TestGenerationErrorResponse(
                success=False,
                error=result.get("error", "Unknown error occurred"),
                error_code="GITLAB_GENERATION_FAILED",
                processing_messages=result.get("processing_messages", [])
            )
            logger.error(f"GitLab test generation failed: {result.get('error')}")
            return JSONResponse(status_code=400, content=error_response.dict())
            
    except Exception as e:
        logger.error(f"Unexpected error in generate_from_gitlab: {e}", exc_info=True)
        error_response = TestGenerationErrorResponse(
            success=False,
            error=str(e),
            error_code="INTERNAL_ERROR"
        )
        return JSONResponse(status_code=500, content=error_response.dict())


@router.get(
    "/workflow-visualization",
    response_model=Dict[str, Any],
    summary="Get workflow visualization",
    description="Get a visual representation of the test generation workflow"
)
async def get_workflow_visualization(
    orchestrator_service: OrchestratorService = Depends(get_orchestrator_service)
):
    """Get workflow visualization from the orchestrator."""
    try:
        logger.info("Generating workflow visualization")
        visualization = await orchestrator_service.get_workflow_visualization()
        
        return {
            "success": True,
            "visualization": visualization,
            "format": "mermaid",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate workflow visualization: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate workflow visualization: {str(e)}"
        )
